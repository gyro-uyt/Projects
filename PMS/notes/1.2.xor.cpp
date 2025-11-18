/*
The XOR operation (^ in C++) returns:

    1 if the bits are different

    0 if the bits are the same

If you do XOR again with the same key:

    (Original ^ Key) ^ Key = Original
    This property makes XOR good for simple encryption/decryption.
*/
#include <iostream>
#include <string>
using namespace std;

string xorEncryptDecrypt(string text, char key)
{
    string result = "";

    for (char c : text)
    {
        // result = result + c^key;
        result += c ^ key;
    }
    return result;
}

int main()
{
    string message = "hello chan"; // message that gets encrypted or decrypted
    char key = 'x';                // Any char key, with this key our message gets XOR

    string encrypted = xorEncryptDecrypt(message, key);
    cout << encrypted << endl;

    string decrypted = xorEncryptDecrypt(encrypted, key);
    cout << "\nDecrypted: " << decrypted << endl;

    return 0;
}