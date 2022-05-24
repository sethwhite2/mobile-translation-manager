Setup
====
Example `config.json` file:
```
{
    "string_index_filename": "string_index.json",
    "sheets_api": {
        "spreadsheet_id": "<sheet id from url>"
    },
    "applications": [
        {
            "platform": "android",
            "project_dir": "path/to/android/project",
            "strings_filename": "strings.xml",
            "languages": [
                "",
                "es-rMX", 
                "es-rEC",
                "es-rES"
            ],
            "default_language": "",
            "string_dirs": [
                "path/to/each/strings/dir"
            ]
        },
        {
            "platform": "ios",
            "project_dir": "path/to/ios/project",
            "strings_filename": "Localizable.strings",
            "languages": [
                "en",
                "es-MX", 
                "es-EC",
                "es-ES"
            ],
            "default_language": "",
            "string_dirs": [
                "path/to/each/strings/dir"
            ]
        }
    ]
}
```

Usage
====
Init
----
```
>>> from mtm import manager
>>> manager.init("config.json")
```
This will create an index file of your current translations.

Sync
----
```
>>> from mtm import manager
>>> manager.sync("config.json")
```
This will sync the index file with all the translations from your applications and the google sheet.

Save
----
```
>>> from mtm import manager
>>> manager.save("config.json")
```
This will save all the translations in the index file to your application's project.

Deploy
----
```
>>> from mtm import manager
>>> manager.deploy("config.json")
```
This will deploy all the translations in the index file to the google sheet.
