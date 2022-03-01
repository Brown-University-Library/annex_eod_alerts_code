# annex_eod_alerts_code

## overview

This code reconciles the list of the Annex end-of-day barcodes produced by the GFA inventory-control software -- with our Alma ILS.

More detail coming.

Note: The check for new-files looks for end-of-day-report files with certain prefixes, archives the originals, then processes the files, then deletes the originals. Note that there are other very similarly-named end-of-day-report files which are not processed or deleted.

---

## installation

(adjust as desired)

- initial setup...

    ```
    % mkdir ./annex_eod_alerts_stuff

    % cd ./annex_eod_alerts_stuff/
    ```

- clone code...

    ```
    % git clone git@github.com:Brown-University-Library/annex_eod_alerts_code.git
    ```

    ...or, for read-only access...

    ```
    % git clone https://github.com/Brown-University-Library/annex_eod_alerts_code.git
    ```

- setup venv...

    ```
    % python3 -m venv ./env
    ```

- load up venv...

    ```
    % cd ./annex_eod_alerts_code/

    % source ../env/bin/activate

    % pip install pip --upgrade

    % pip install -r ./requirements/requirements.txt
    ```

- setup venv-settings...

    add required settings to bottom of env/bin/activate file via lines like...

    `export FOO="bar"`

    ...or load a file of settings by adding, to  bottom of env/bin/activate file, a line like...

    `source "/path/to/env_settings.sh"`

- load the venv-settings...

    now activating the venv will provide access to packages _and_ settings...

    ```
    % source ../env/bin/activate
    ```

---
