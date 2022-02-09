"""
Manages processing.

Steps (roughly)...
- Determine if there are new files to process. Assuming there are...
- Archive each of the files (with timestamp in filename).
    - Alert folk if there are file-name issues.
- set up alerts-holder and four data-holders
- Process each file...
    - barcode check
    - process-type, location, status-check
    - build alert-list and store it
    - build data-summary and store it
- ? Save alerts and data-holders?
- Email alert and data-holders as attachments.
"""

