#include <iostream>
#include <fstream>
using namespace std;

int main()
{
    cout << "Welcome to PASSWORD MANAGEMENT SYSTEM" << endl;

    ofstream storeDAta("../data/1.0.txt", ios::app);

    string cr_username;
    string cr_description;
    string cr_password;

    cout << "Enter the username to be registered: ";
    getline(cin, cr_username);
    cout << "Enter the password to be registered: ";
    getline(cin, cr_password);
    cout << "Enter the description to be registered: ";
    getline(cin, cr_description);

    char breakline = ' ';

    storeDAta << cr_username;
    storeDAta << endl;
    storeDAta << cr_password;
    storeDAta << endl;
    storeDAta << cr_description;
    storeDAta << endl<<endl;

    return 0;
}