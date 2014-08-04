import requests
import json

class SpittalPond():
    base_url = "http://tmrbmub01prd:8000"
    is_logged_in = False
    pub_user = "root"
    def do_request(self, url, in_data, in_file=None):
        url_string=url
        header={"content-type":"application/x-www-form-urlencoded"}
        str_response=requests.post(url_string, data=in_data,) #headers=header);
        return str_response

    def do_login(self, user, password):
        in_data = ""
        url = ""
        
        in_data = """{{ "username":"{username}", "password":"{password}" }}""".format(username=user, password=password)
        
        url = self.base_url + "/oasis/login"
        
        str_response = self.do_request(url, in_data)
        json_response = json.loads(str_response.content)
        
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
            print("You are logged into Mid-tier")
