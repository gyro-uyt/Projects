#include <iostream>
#include <string>
#include <fstream>
using namespace std;

void print(string in)
{
    for(char c:in)  // For every character c in the string fullContent, print its ASCII value followed by a space.
    {
        cout<< int(c)<<" ";
    }
    cout<<endl;
}
int main()
{
    string target = "helloBillo";
    string key = "wow";

    cout<<"message: ";
    print(target);
    cout<<"key: ";
    print(key);
    
    // size_t is an unsigned integer type used for sizes and indexing, especially with strings and containers.
    // Unlike int, it can't be negative and is safer for handling .length() or .size().
    for (size_t i = 0; i < target.length(); i++)
    {
        target[i] = target[i] ^ key[i % key.length()];
        /*`
        key[i % key.length()] this repeats the key until the operation is over
        The modulo operator (%) gives the remainder when you divide.
        So:
        i = 0 → 0 % 3 = 0 → key[0] = 'k'
        
        i = 1 → 1 % 3 = 1 → key[1] = 'e'
        
        i = 2 → 2 % 3 = 2 → key[2] = 'y'
        
        i = 3 → 3 % 3 = 0 → key[0] = 'k' again
        
        i = 4 → 4 % 3 = 1 → key[1] = 'e'
        And so on...
        hence, it will keep cycling until the loop is over
        */
    }

    cout<<"emcrypted: ";
    print(target);

    return 0;
}