Querys = {
    # Top 10 Attackers
    "Attackers": {
        "aggs": {
            "2": {
                "terms": {"field": "originIp", "size": 10, "order": {"_count": "desc"}}
            }
        },
        "size": 0,
        "_source": {"excludes": []},
        "stored_fields": ["*"],
        "script_fields": {},
        "docvalue_fields": [
            {"field": "insertedDate", "format": "date_time"},
            {"field": "logDate", "format": "date_time"},
            {"field": "normalDate", "format": "date_time"},
        ],
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"msgClassName": {"query": "attack"}}},
                    {"match_phrase": {"directionName": {"query": "external"}}},
                    {
                        "range": {
                            "normalDate": {
                                "gte": 1699039990134,
                                "lte": 1699648390134,
                                "format": "epoch_millis",
                            }
                        }
                    },
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"msgClassName": {"query": "attack"}}},
                    {"match_phrase": {"directionName": {"query": "external"}}},
                ],
                "filter": [{"match_all": {}}, {"match_all": {}}],
                "should": [],
                "must_not": [],
            }
        },
    },
    # Top 10 Vulnerabilities
    "Top10Vulns": {
        "aggs": {
            "2": {
                "terms": {
                    "field": "threatName",
                    "size": 10,
                    "order": {"_count": "desc"},
                }
            }
        },
        "size": 0,
        "_source": {"excludes": []},
        "stored_fields": ["*"],
        "script_fields": {},
        "docvalue_fields": [
            {"field": "insertedDate", "format": "date_time"},
            {"field": "logDate", "format": "date_time"},
            {"field": "normalDate", "format": "date_time"},
        ],
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}},
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"msgClassName": {"query": "vulnerability"}}},
                    {
                        "range": {
                            "normalDate": {
                                "gte": 1699039990134,
                                "lte": 1699648390134,
                                "format": "epoch_millis",
                            }
                        }
                    },
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"msgClassName": {"query": "vulnerability"}}},
                ],
                "filter": [{"match_all": {}}],
                "should": [],
                "must_not": [
                    {
                        "match_phrase": {
                            "msgSourceTypeName": {"query": "syslog - darktrace cef"}
                        }
                    },
                    {
                        "match_phrase": {
                            "msgSourceTypeName": {"query": "syslog - darktrace cef"}
                        }
                    },
                ],
            }
        },
    },
    # Top 10 Audit Violations
    "AuditViolations": {
        "aggs": {
            "2": {
                "terms": {
                    "field": "commonEventName",
                    "size": 10,
                    "order": {"_count": "desc"},
                },
                "aggs": {
                    "3": {
                        "terms": {
                            "field": "login",
                            "size": 5,
                            "order": {"_count": "desc"},
                        }
                    }
                },
            }
        },
        "size": 0,
        "_source": {"excludes": []},
        "stored_fields": ["*"],
        "script_fields": {},
        "docvalue_fields": [
            {"field": "insertedDate", "format": "date_time"},
            {"field": "logDate", "format": "date_time"},
            {"field": "normalDate", "format": "date_time"},
        ],
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}},
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {
                        "bool": {
                            "should": [
                                {
                                    "match_phrase": {
                                        "msgClassName": "authentication failure"
                                    }
                                },
                                {"match_phrase": {"msgClassName": "misuse"}},
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    {
                        "range": {
                            "normalDate": {
                                "gte": 1699039990134,
                                "lte": 1699648390134,
                                "format": "epoch_millis",
                            }
                        }
                    },
                    {"match_phrase": {"entityName": {"query": "ensa ti"}}},
                    {
                        "bool": {
                            "should": [
                                {
                                    "match_phrase": {
                                        "msgClassName": "authentication failure"
                                    }
                                },
                                {"match_phrase": {"msgClassName": "misuse"}},
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ],
                "filter": [{"match_all": {}}],
                "should": [],
                "must_not": [],
            }
        },
    },
}
