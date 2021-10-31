from flask import Flask,request
from flask.json import jsonify
from flask_restful import Api,Resource
from difflib import SequenceMatcher


app=Flask(__name__)
api=Api(app)

class AddressUpdate(Resource):
    
    #HTTP request to API Supports only GET method

    def get(self):

        #Fetching address data from HTTP request body
        data= request.get_json()

        #Making a copy of original address for future use
        copy=dict(data)

        address=[]
        
        #Storing different fields of the address as elements of a list (array)
        for item in data:
            
            #All items have been converted to avoid ambiguity and for ease of computation.
            if item!=item.lower():
                data[item.lower()]=data[item].lower()
                del data[item]
                address.append(data[item.lower()])
            else:
                data[item]=data[item].lower()
                address.append(data[item])

        state=data["state"]
       
        #Formatting the address
        new_address= self.formatter(address,state)

        address2=new_address["Formatted Address"].split(',')
        final_address=[]

        
        #The final address must adhere to a proper format which starts from building number and ends at Pincode.
        #We compare the user's input with a pre-defined template to ensure the above condition.
        
        template=["pincode","state","district","sub district","vtc","locality","landmark","street","building"]
        out_address={"Formatted Address":""}
        
        #Below iterator generates a clean Addess string after it has been formatted.
        
        for i in template:
            for j in copy:
                if j.lower()==i and i!="pincode" and i!="building" and data[i] in address2:
                    if copy[j] not in final_address:
                        final_address.append(copy[j])
                        final_address.append(",")
                        out_address[i]=copy[j]
                elif i=="pincode" and j.lower()=="pincode":
                    final_address.append(copy[j]+'.')
                    out_address[i]=copy[j]
                elif i=="building" and j.lower()=="building":
                    final_address.append(copy[j])
                    out_address[i]=copy[j]
        
        '''As the template was reversed top to bottom, we need to reverse it back in bottom to top form of address, 
        where bottom level is building and top level is pincode.'''
        
        for i in reversed(final_address):
            out_address["Formatted Address"]+= i+ " "
            
        #Send back Formatted address in json format
        return jsonify(out_address)


    def formatter(self,data,state):

        new_address=""
        for i in range (len(data)-1):
            for j in range(i+1,len(data)):

                #If any two parts of the address are exactly same, then one must be merged
                if SequenceMatcher(None,data[i],data[j]).ratio()==1.0:
                    if data[j]==state:
                        data[i]=""
                    else:
                        data[j]=""

                #If two parts of the address are very similar, then they must be merged, provided State is not merged
                elif SequenceMatcher(None,data[i],data[j]).ratio()>=0.90 and data[j]!=state:
                    data[i]=""


        #Adding punctuator in Address
        for elem in data:
            new_address+=elem.strip()+","
        return({"Formatted Address":new_address})

api.add_resource(AddressUpdate,"/addressFormat")

if __name__=="__main__":
    app.run(debug=True)
