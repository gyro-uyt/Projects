/*
xor operation ( ^ ),
return 0 ---> both bits are same
return 1 ---> bits are different

->  A ⊕ B ⊕ B = A
That means, if you XOR some data with a key to encrypt it, and then XOR it again with the same key, you get your original data back!
*/
#include <iostream>
using namespace std;

int main()
{
    char ans = 'm';
    char key = 'k';

    char xo = ans^key;

    cout << "ans = "<< ans <<endl;
    cout << "key = "<< key <<endl;
    cout << "xo = "<< (int)xo <<endl;   // char xo isn't printing bcz. it's ascii value is 15 which contain a non-printable character

    return 0;
}