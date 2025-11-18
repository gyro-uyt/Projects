
# Plans

v1.1 → A basic PMS.  

v1.2 → Encrypt passwords with XOR (simple obfuscation).  

v1.3 → Add a option to add credentials in the view profile.  

v1.4 → Implement separate delete profile feature.  

v1.5 → Add profile rename/update credential features.  

v1.6 → Modular programming

v2.0 → Hash master passwords using libraries or own logic.  

v2.1 → Secure console input (hide password input).  

v2.2 → Export/import credentials.  

v3.0 → GUI

🆕 Feature Ideas  

    Edit Stored Profile
    
    Password Masking  
        When the user types a password, don’t display it (use getch() on Windows or termios on Linux).  

    Profile Key Hashing  
        Instead of using the key directly for XOR, store a hash of the key (e.g., using SHA256) and only proceed if the entered key matches.  

    Search Credentials  
        Add a feature to search for credentials by website or description.  

    Update Credential  
        Allow the user to update username/password for an existing service.  

    Use JSON instead of raw text (optional but modern):  
        Makes parsing, updating and displaying data much easier and structured.  

    Add Master Password to Enter the App  
        Before accessing menu, require a master password that encrypts/decrypts the rest.  
