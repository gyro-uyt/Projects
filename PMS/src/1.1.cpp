#include <iostream>
#include <fstream>
#include <filesystem>   // used to interact with the file system — like folders, files, paths, etc.
#include <string>
#include <vector>
using namespace std;
namespace fs = std::filesystem;

class PMS
{
private:
    string cr_username;
    string cr_description;
    string cr_password;
    string profile_name;
    string profile_name_path; // this is same as profile_name, i used this to create the .txt file, whose name is given by user
    string master_password;
    int menu_choice;
    int profile_choice; // menu choice, Change name
    int choose_profile;

public:
    void welcomeMsg();
    void setProfile(); // stores Profile name, Master-password
    int storeProfile();
    void setCredential();
    void storeCredential();
    void run();
    int menu();
    int chooseProfile();
};
void PMS::welcomeMsg()
{
    cout << "\n! Welcome to the PASSWORD MANAGEMENT SYSTEM !" << endl;
}
void PMS::setProfile()
{
    cout << "Set the Profile nickname (without any white spaces): ";
    cin.ignore(numeric_limits<streamsize>::max(), '\n'); // clears any leftover newline
    getline(cin, profile_name);
    profile_name_path = profile_name;
    cout << "Set the master-password: ";
    getline(cin, master_password);
}
int PMS::storeProfile()
{
    // Storing only the profile names everytime they are created
    ofstream StoreAllProfiles("../data/AllProfileData.txt", ios::app);
    StoreAllProfiles << profile_name << endl;
    StoreAllProfiles.close();

    // Define path to data folder (relative to where the program runs)
    string folderPath = "../data";

    // Check if "data" folder exists, if not create it
    if (!fs::exists(folderPath)) //  checks whether the folder already exists
    {
        if (!fs::create_directory(folderPath)) // tries to create the folder (only runs if it doesn’t already exist)
        {
            cerr << "Failed to create folder: " << folderPath << endl;
            return 1;
        }
    }
    profile_name_path = folderPath + "/1.1." + profile_name_path + ".txt";

    ofstream storeProfileData(profile_name_path, ios::app); // Note: using new Constructor method
    storeProfileData << profile_name;
    storeProfileData << endl;
    storeProfileData << master_password;
    storeProfileData << endl
                     << endl;
    return 0;
}
void PMS::setCredential()
{
    cout << "\nEnter the username to be registered: ";
    cin.ignore();
    getline(cin, cr_username);
    cout << "Enter the password to be registered: ";
    getline(cin, cr_password);
    cout << "Enter the description to be registered: ";
    getline(cin, cr_description);
}
void PMS::storeCredential()
{
    ofstream storeCredentialDAta(profile_name_path, ios::app);
    storeCredentialDAta << cr_username;
    storeCredentialDAta << endl;
    storeCredentialDAta << cr_password;
    storeCredentialDAta << endl;
    storeCredentialDAta << cr_description;
    storeCredentialDAta << endl
                        << endl;
    storeCredentialDAta.close();
}
void PMS::run()
{
    menu();
    // setCredential();
    // storeCredential();
}
int PMS::menu()
{
    welcomeMsg();
    cout << "\nChoose the operation to be followed:\n";
    cout << "1. View a Stored profile\n";
    cout << "2. Create a New profile\n";
    cout << "3. Exit\n";

    cin >> menu_choice;
    switch (menu_choice)
    {
    case 1:
        chooseProfile();
        break;

    case 2:
        cout << "\nCreating a new Profile:\n";
        setProfile();
        storeProfile();
        cout << "\nProfile created successfully\n";

        while (1)
        {
            cout << "1. Add credentials\n";
            cout << "2. exit\n";
            cin >> profile_choice;
            switch (profile_choice)
            {
            case 1:
                setCredential();
                storeCredential();
                cout << "\nStored entered credential successfully\n";
                break;
            case 2:
                return 0;
                break;
            default:
                break;
            }
        }
        break;

    case 3:
        return 0;
        break;

    default:
        cout << "Submit your response in intgers 1,2,3 only!\n";
        break;
    }
    return 0;
}
int PMS::chooseProfile()
{
    ifstream openProfileFile("../data/AllProfileData.txt");
    vector<string> allProfileNames;
    string names;
    cin.ignore();
    while (getline(openProfileFile, names)) // reads one line at a time from the 'openProfileFile' and puts it in the 'names' variable
    {
        allProfileNames.push_back(names); // each time loop is ran 'names' stores all lines, and we push those into 'allProfileNames' vector
    }
    // Now, we have successfully read the 'StoredProfiles.txt' file and stored all of it's name into a vector

    // Now, we make menu to choose profile from this vector
    cout << "\nChoose one of the stored Profile: " << endl;
    for (int i = 0; i < allProfileNames.size(); i++)
    {
        cout << (i + 1) << ". " << allProfileNames[i] << endl;
    }
    cin >> choose_profile;
    cin.ignore();

    // Now, Open the selected file and show data
    string selectedProfile = allProfileNames[choose_profile - 1];               // this is the file choosed by the user
    string selectedProfileFileName = "../data/1.1." + selectedProfile + ".txt"; // this is it's address

    // retrive the master-password
    ifstream retriveMasterPassword(selectedProfileFileName);
    int master_password_line = 2;
    int current_line = 1;
    while (getline(retriveMasterPassword, master_password))
    {
        if (current_line == master_password_line)
        {
            break;
        }
        current_line++;
    }
    retriveMasterPassword.close();

    // cross-verifying master password
    string check_master_password;
    cout << "\nEnter the Master password for the choosen profile: ";
    cin >> check_master_password;
    if (check_master_password == master_password)
    {
        cout << "Authentication Verified!" << endl;
    }
    else
    {
        cout << "User Authentication Failed!" << endl;
        return 0;
    }

    // displaying the content
    ifstream profileFile(selectedProfileFileName);
    string displayLines;
    cout << "\nDisplaying the content stored in the choosed profile\n";
    while (getline(profileFile, displayLines))
    {
        cout << displayLines << endl;
    }
    return 0;
}

int main()
{
    PMS alpha;
    alpha.menu();

    return 0;
}