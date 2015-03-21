import struct
import sys
import zlib

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    try:
        from StringIO import StringIO as BytesIO
    except ImportError:
        from io import BytesIO

try:
    import snappy
except ImportError:
    snappy = None


COMPRESSION_UNCOMPRESSED = 0
"""Uncompressed compression format.
"""

COMPRESSION_ZLIB = 1
"""ZLIB compression format.
"""

COMPRESSION_SNAPPY = 2
"""Snappy compression format.
"""


def write_header_v1(f, compression):
    """Write an Akaibu version 1 log file header.

    :param f: Output file.
    :param compression: Compression.
    :type compression: int
    """

    if compression not in {COMPRESSION_UNCOMPRESSED,
                           COMPRESSION_ZLIB,
                           COMPRESSION_SNAPPY}:
        raise NotImplementedError('Unsupported compression: %r' %
                                  (compression))

    f.write(b'AKAI\x01' + bytes(bytearray((compression, ))) + b'\x00\x00')


def write_record_v1(f, data):
    """Write an Akaibu version 1 record.

    :param f: Output file.
    :param data: Data.
    :type data: str
    """

    # Write the record size.
    size = len(data)

    if size < 128:
        size_data = bytearray((size, ))
    else:
        packed = bytearray(struct.pack('>Q', size))

        if size < 2 ** 14:
            size_data = packed[-2:]
            size_data[0] |= 0b10000000
        elif size < 2 ** 21:
            size_data = packed[-3:]
            size_data[0] |= 0b11000000
        elif size < 2 ** 28:
            size_data = packed[-4:]
            size_data[0] |= 0b11100000
        elif size < 2 ** 35:
            size_data = packed[-5:]
            size_data[0] |= 0b11110000
        else:
            raise NotImplementedError('Akaibu version 1 does not support '
                                      'records over %d B' %
                                      (2 ** 35 - 1))

    f.write(bytes(size_data))

    # Write the data.
    f.write(bytes(data))


SAMPLE_SEQUENCE = bytearray(i for i in range(0, 256))


def get_sample_data(size):
    """Get sample data.

    :param size: Data size.
    :type size: int.
    :returns:
        a data sample of the given length of repeating sequences of 0x00-0xff.
    """

    repeats = size // 256
    end = size - repeats * 256

    return SAMPLE_SEQUENCE * repeats + SAMPLE_SEQUENCE[:end]


# Parse command line arguments.
arg_set = frozenset(sys.argv[1:])


def show_usage():
    sys.stderr.write('Usage: %s [number of records in 100 B increments '
                     '(default 10)]\n' % (sys.argv[0]))
    exit(1)

if '--help' in arg_set or '-h' in arg_set or '-?' in arg_set:
    show_usage()

if len(sys.argv) > 2:
    sys.stderr.write('Invalid number of arguments.\n\n')
    show_usage()

sample_record_count = 10
if len(sys.argv) > 1:
    try:
        sample_record_count = int(sys.argv[1])
    except ValueError:
        sys.stderr.write('Invalid number of records: %s\n\n' % (sys.argv[1]))
        show_usage()

# Generate sample record data.
sample_record_stream = BytesIO()
for size in range(100, 100 * sample_record_count, 100):
    write_record_v1(sample_record_stream, get_sample_data(size))
sample_records = sample_record_stream.getvalue()

# Generate uncompressed sample.
with open('uncompressed.v1.akaibu', 'wb') as f:
    write_header_v1(f, COMPRESSION_UNCOMPRESSED)
    f.write(sample_records)

# Generate zlib compressed sample.
with open('zlib.v1.akaibu', 'wb') as f:
    write_header_v1(f, COMPRESSION_ZLIB)
    f.write(zlib.compress(sample_records, 9))

# Generate Snappy compressed sample.
if snappy:
    with open('snappy.v1.akaibu', 'wb') as f:
        write_header_v1(f, COMPRESSION_SNAPPY)
        f.write(snappy.StreamCompressor().compress(sample_records))
