# Akaibu log archival format specification

Akaibu, from the Japanese アーカイブ (Ākaibu), is a log archival format for arbitrary log records. The format specification for version 1 is contained in [format.rst](format.rst).


## Samples

The Akaibu format specification repository includes the ability to generate sample files. Install the requirements and use Make:

    $ pip install -r requirements.txt
    $ make samples

**Note:** Snappy compressed samples are only generated if the Snappy library is installed.
