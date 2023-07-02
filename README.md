# The goal of the tool is to limit applications and safari web sites usage by providing a set of rules.

## Installation guide.
Works only on Mac OS. Tested with python 3.9 and mac os monterey. 
All the requirements are in requirements.txt

## This is an example config with some comments
```
{
    //Urls that will always be whitelisted
    "whilelist_urls": [
        "https://stackoverflow.com"
    ],
    //List of strings that will make a web page white listed if it is present in the title of the page
    "whilelist_names": [
        "python"
    ],
    //Full blackout means, that during provided timeframe all blacklisted links and apps will be closed without any checks
    //Values are in seconds
    "fullBlackout": { 
        "start": 0,
        "duration": 0
    },
    //Full release means that counter will be updated but applications/web pages won't be closed
    //Values are in seconds
    "fullRelease": {
        "start": 0,
        "duration": 0
    },
    //Urls that will be blacklisted in Safari
    //"limit" - number of minutes allowed per day
    //"full_domain_name" if set true will match all urls that are substring of given url
    //"full_domain_name" if set false will require exact match of urls
    //"time_intervals" - interval when access is allowed . limits will be applied anyway
    "blacklist_urls": [{
        "url": "https://www.instagram.com",
        "limit": 15,
        "full_domain_name": true,
        "time_intervals": [{
                "start": "10:00",
                "end": "11:00"
            },
            {
                "start": "18:00",
                "end": "22:00"
            }
        ]
    },
    {
        "url": "https://www.facebook.com",
        "limit": 15,
        "full_domain_name": false,
        "time_intervals": [{
                "start": "10:00",
                "end": "11:00"
            },
            {
                "start": "18:00",
                "end": "21:00"
            }
        ]
    }],
    //Similar to blacklisted. Focused application is counted as active
    "applications": [{
        "application": "Telegram",
        "limit": 10,
        "time_intervals": [{
                "start": "10:00",
                "end": "11:00"
            },
            {
                "start": "18:00",
                "end": "21:00"
            }
        ]
    }]
}
```
