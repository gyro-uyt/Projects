#include <iostream>
#include <fstream>
#include <string>
using namespace std;

void xorFunc(string &msg, string &key)
{
    for (size_t i = 0; i < msg.length(); i++)
    {
        msg[i] = msg[i] ^ key[i % key.length()];
    }
}

int main()
{
    string key = "by";
    string fileName="02.2.txt";
    string line, fullContent;

    // read full file
    ifstream read(fileName);
    if (!read)
    {
        cerr<<"Error: Could not the opened the file for reading."<<endl;
        return 1;
    }

    while (getline(read, line))
    {
        fullContent = fullContent + line + "\n";
    }
    read.close();

    // encrypt
    xorFunc(fullContent, key);

    // overWrite file with encrypted content
    ofstream write(fileName);
    if (!write)
    {
        cerr<<"Error: Opening the file for encrypting the data in it."<<endl;
    }
    write << fullContent;
    write.close();

    cout<<"File Encrypted Successfully\n";

    return 0;
}