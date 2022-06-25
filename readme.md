
# Cisco Umbrella integration with Arcsight via API

Sample parser script for cisco umbrella logs - CSV to CEF - for cisco umbrella integration with Arcsight.

# Requirements
In order to use the script:                 
    1- You will need to get cisco umbrella organizaton ID.           
    2- Add os enviroment varaible, ciscoUmbrellaUserName is a key & cisco umbrella's username as a value.        
    3- Add os enviroment varaible, ciscoUmbrellaPassword is a key & cisco umbrella's password as a value.

# Notes
1- Cisco API displays only the "Blocked" logs.            
2- The script is built to parse Cisco Umbrella logs from the web & map the output CSV into CEF format then deliver it to ArcSight as a CEF file.  
3- API call to fetch all logs between the current moment and the last 15 mins.

# Instruction:
install all the required package:             
pip install -r requirements.txt                  
python cisco_umbrella -o <organization_id>                   
