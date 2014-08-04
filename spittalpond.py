import requests
import json

class SpittalPond():
    base_url = "http://tmrbmub01prd:8000"
    is_logged_in = False
    pub_user = "root"
    cookies = None
    def do_request(self, url, in_data=None, in_file=None):
        url_string=url
        header={"content-type":"application/x-www-form-urlencoded"}
        response=requests.post(
            url_string,
            data=in_data,
            cookies=self.cookies  #For Authentication!
        ) #headers=header);
        return response

    def do_login(self, user, password):
        in_data = ""
        url = ""
        
        in_data = """{{ "username":"{username}", "password":"{password}" }}""".format(username=user, password=password)
        
        url = self.base_url + "/oasis/login"
        
        
        response = self.do_request(url, in_data)
        json_response = json.loads(response.content)
        
        #This is used for debugging HTNML outputs.
        #display(HTML(strResponse.content))
        
        #InitScriptEngine
        #Set JsonObject = DecodeJsonString(CStr(strResponse))
        #value = GetProperty(JsonObject, "success")
        
        
        value = json_response["success"]
        if value == False:
            print("Invalid user id or password")
        else:
            #writetoconsole objHTTP.GetResponseHeader("Set-Cookie")
            self.cookies = dict(sessionid=response.cookies['sessionid'])
            print("You are logged into Mid-tier")
