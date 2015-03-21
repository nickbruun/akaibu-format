Akaibu log archival format
==========================

Akaibu, from the Japanese アーカイブ (Ākaibu), is a log archival format for arbitrary log records.


Storage format (v1)
-------------------

Akaibu log files (by convention denoted by the ``.akaibu`` file name extension) consist of two parts: a fixed length header and a record stream of records of up to 32 GiB - 1 B:

::

     0  1  2  3  4  5  6  7
   +--+--+--+--+--+--+--+--+
   | Header                |
   +--+--+--+--+--+--+--+--+
   / Record stream         /
   +--+--+--+--+--+--+--+--+


Header
~~~~~~

The header (8 octets) contains information about the log file, structured as follows:

============ ============= ====================================================
Description  Size (octets) Notes
============ ============= ====================================================
Magic header             4 'AKAI'
Version                  1 Version (unsigned 8 bit integer). ``1``
                           for version 1.
Compression              1 Record stream compression format (unsigned 8 bit
                           integer). Valid values are:

                           ``0``
                              Uncompressed
                           ``1``
                              zlib (RFC 1950)
                           ``2``
                              Snappy (using `framing <https://code.google.com/p/snappy/source/browse/trunk/framing_format.txt>`_)
Reserved                 2 *64-bit word alignment.* Must be ``NUL`` bytes.
============ ============= ====================================================

.. note::

   The header contains no information about the size of the record stream to
   allow continuous writing of records to a log file.


Record stream
~~~~~~~~~~~~~

The record stream is simply a non-padded stream of records optionally compressed by the compression format indicated in the header. A record is represented by a size followed by the record data:

=========== ============= =====================================================
Description Size (octets) Description
=========== ============= =====================================================
Size                  1-5 Record size as a `variable-length unsigned integer.`__
Data                    ? Record data.
=========== ============= =====================================================

A stream of three records of 5, 191 and 45,182 octets respectively would be laid out as follows:

::

         0      1      2      3      4      5      6      7
   +------+------+------+------+------+------+------+------+
   | 0x05 | Data (record #1)                 | 0x80   0xbf |
   | Data (record #2)                                      |
   / ..                                                    /
   | ..                                             | 0xc0 |
   | 0xb0   0x7e | Data (record #3)                        |
   / ..                                                    /
   | ..                                      |
   +------+------+------+------+------+------+

__ varint_


Data types
~~~~~~~~~~

.. _varint:

Variable-length unsigned integers
'''''''''''''''''''''''''''''''''

To optimize the storage size of a record stream, Akaibu uses a variable-length unsigned integer encoding. A variable-length unsigned integer is encoded in big endian byte order in 1-5 octets, with the first octet identifying the size of the value by its prefix:

=========== ============= ========= ============== ============================
Prefix bits Size (octets) Data bits Unsigned range Size range
=========== ============= ========= ============== ============================
``0``                   1         7 127            127 B
``10``                  2        14 16,383         ~15.999 KiB
``110``                 3        21 2,097,151      ~2.000 MiB
``1110``                4        28 268,435,455    ~256.000 MiB
``11110``               5        35 34,359,738,367 ~32.000 GiB
=========== ============= ========= ============== ============================

The value can be obtained by simply determining the complete integer from its prefix and masking out the prefix bits.
