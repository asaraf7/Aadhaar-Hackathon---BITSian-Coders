from flask import Flask,request
from flask.json import jsonify
from flask_restful import Api,Resource
from difflib import SequenceMatcher


app=Flask(__name__)
api=Api(app)

class AddressUpdate(Resource):

    def get(self):

        #Fetching address data from HTTP request body
        data= request.get_json()

        #Making a copy of original address for future use
        copy=dict(data)

        address=[]
        
        #Storing different fields of the address as elements of a list (array)
        for item in data:
            
            if item!=item.lower():
                data[item.lower()]=data[item].lower()
                del data[item]
                address.append(data[item.lower()])
            else:
                data[item]=data[item].lower()
                address.append(data[item])

        state=data["state"]
        print(copy)
        print(address)

       
        #Formatting the address
        new_address= self.formatter(address,state)


        address2=new_address["Formatted Address"].split(',')
        final_address=[]

        print(address2)
        template=["building","street","landmark","locality","vtc","sub district","district","state","pincode"]
        
        for i in template:
            for j in copy:
                if j.lower()==i and i!="pincode" and data[i] in address2:
                    c=address2.index(data[i])
                    if copy[j] not in final_address:
                        final_address.append(copy[j])
                        final_address.append(",")
                elif i=="pincode" and j.lower()=="pincode":
                    final_address.append(copy[j]+'.')

        #Send back Formatted address in json format

        print(final_address)
        
        out_address={"Formatted Address":""}
        for i in final_address:
            out_address["Formatted Address"]+= i+ " "
        return jsonify(out_address)


    def formatter(self,data,state):

        print(data)

        new_address=""
        for i in range (len(data)-1):
            for j in range(i+1,len(data)):

                #If any two parts of the address are exactly same, then one must be merged
                if SequenceMatcher(None,data[i],data[j]).ratio()==1.0:
                    data[i]=""

                #If two parts of the address are very similar, then they must be merged, provided State is not merged
                elif SequenceMatcher(None,data[i],data[j]).ratio()>=0.90 and data[j]!=state:
                    data[i]=""
                elif (' po' in data[j] or ' ps' in data[j]) and (SequenceMatcher(None,data[i],data[j]).ratio()>0.6):
                    data[j]=""
                elif (' po' in data[i] or ' ps' in data[i]) and (SequenceMatcher(None,data[i],data[j]).ratio()>0.6):
                    data[i]=""


        #Adding punctuator in Address
        for elem in data:
            new_address+=elem.strip()+","
        return({"Formatted Address":new_address})

api.add_resource(AddressUpdate,"/addressFormat")

if __name__=="__main__":
    app.run(debug=True)
