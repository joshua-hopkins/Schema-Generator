import os, json
from tqdm import tqdm

# Schema Generator

# Main function
def main(): 
    # Variables:
    outputPath = os.getcwd()
    collection = ""
    fieldName = ""
    requiredList = []
    fields = {}

    print("Schema Generator\n")

    # Get the path name
    path = input("Please insert the path name: ")
    directory = os.listdir(path)

    print("\nAvailable Files: \n")

    # List the files in the directory
    for files in directory:
        print(files)

    print("Now generating files based off the directory.")

    for i in tqdm (range (1), desc = "Generating..."):
        for fileToRead in directory:
            # Reset Everything
            os.chdir(path)
            requiredList.clear()
            fields.clear()

            # Reading from the file
            with open (fileToRead, 'rt') as myFile:
                for line in myFile:
                    if ("collection" in line): # Check for collection names
                        collection = line.removeprefix('@Document(collection = ').rstrip().removesuffix(")").strip('"') # Strip any unnecessary characters
                    elif ("private String" in line): # Check for the bsonType: String
                        if ("@Id" not in line): # We don't need the id
                            fieldName = line.strip().removeprefix('@Indexed ').removeprefix('private String ').strip(';') # Strip any unnecessary characters
                            requiredList.append(fieldName)
                            fields.update({fieldName: {"bsonType" : "string", "description" : "Must be a string and is required"}}) # Turn the info into a dictionary and add it to the main dictionary
                # print(collection)
            validator = schema_gen(fields, collection, requiredList) # Send the dictionary of fields into the generator

            os.chdir(outputPath)

            line1 = "// Instance: ***INSERT INSTANCE***\n"
            line2 = "// Database: ***INSERT DB***\n\n"
            line3 = "db = db.getSiblingDB('***INSERT DB***')\n\n"
            line4 = "db.runCommand(\n{schemaFile}\n)".format(schemaFile=json.dumps(validator, indent=5))

            print("load(pwd() + '/***INSERT DB***Validation/***INSERT DB***_"+collection+"_validation.js')")
            # Write the information to a file
            with open("***INSERT DB_" + collection + "_validation.js", "w") as output:
                output.writelines([line1, line2, line3, line4])
    
    print("Complete")
    
# Schema Function
def schema_gen(fields, collectionName, required):
    schema = {
        "collMod": collectionName,
        "validator": {
            "$jsonSchema": {
                "bsonType": "object", 
                "required": required,
                "properties": {}
            }
        },
        "validationLevel": "moderate",
        "validationAction": "warn"
    }

    for i in fields:
        schema["validator"]["$jsonSchema"]["properties"].update(
            {
                i: {
                    "bsonType": fields[i]["bsonType"],
                    "description": fields[i]["description"]
                }
            }
        )

    return schema

main()
