import time
class ciscoUmbrellaConstant():
    def __init__(self,org_number):
        self.filename = 'CiscoUmbrellaReport-' + str(time.strftime("%Y%m%d-%H%M%S"))
        self.org_number = org_number
    
        self.header= {
            'Host': 'login.umbrella.com',
            'Content-Type': 'application/x-www-form-urlencoded'
            }

        self.org_info= {
            'Host': 'dashboard.umbrella.com',
            'Referer': 'https://login.umbrella.com/'
            }

        self.bearer_token={
            'Host': 'management.api.umbrella.com',
            'Referer': 'https://dashboard.umbrella.com/',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
             }
        self.activity_search= {
            'Host': 'reports.api.umbrella.com',
            'Referer': 'https://dashboard.umbrella.com/',
            'x-source': 'reporting-app',
            'x-region-redirect': '200',
            'Origin': 'https://dashboard.umbrella.com'
            }

        self.create_csv={
            'Host': 'api.opendns.com',
            'Referer': 'https://dashboard.umbrella.com/',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://dashboard.umbrella.com',
            }

        self.token= {
            'Host': 'dashboard.umbrella.com',
            'Referer': f'https://dashboard.umbrella.com/o/{self.org_number}/',
            'content-type': 'application/json; charset=utf-8'
            }

        self.get_data= {
            'Host': 'export.us.reports.umbrella.com',
            'Referer': 'https://dashboard.umbrella.com/'
        }

        self.urls = {
            "login_url": "https://login.umbrella.com/",
            "org_info": f"https://dashboard.umbrella.com/o/{self.org_number}/",
            "bearer_token": "https://management.api.umbrella.com/auth/v2/oauth2/jwt-bearer/token",
            "activity_search": f"https://reports.api.umbrella.com/v2/organizations/{self.org_number}/activity",
            "create_csv": f"https://api.opendns.com/v3/organizations/{self.org_number}/exportedreportrequests",
            "token": 'https://dashboard.umbrella.com/token'
        }