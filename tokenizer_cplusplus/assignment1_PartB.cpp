/** 
file name: assignment1_PartB.cpp
Author: Kevin Permana
UCInet ID: 50259184
CS121 HW 1 part B
*/
#include <iostream>
#include <unordered_map>
#include <fstream>
#include <cstring>
#include <string>
#include <typeinfo>
#include <ctime>
#include <stdio.h>

using namespace std;

typedef unordered_map<string,int> myMap;

/** findIntersection
	takes two text files as arguments and outputs the number of tokens they have in common.
    @param TextFilePath, string of text file path
    @param TextFilePath2, string of text2 file path
    @return int, number of tokens they have in common
*/
int findIntersection(string TextFilePath, string TextFilePath2)
{
	myMap myTokens;
	ifstream InputFile, InputFile2;
	InputFile.open(TextFilePath);
	if(!InputFile)
    {
    	cout << "File not found! : " << TextFilePath << endl;
        exit(1);
    }
	InputFile2.open(TextFilePath2);
	if(!InputFile2)
    {
    	cout << "File not found! : " << TextFilePath2 << endl;
        exit(1);
    }

	char myChar;
	string line = "";
	int count = 0; //number of intersections

	InputFile.unsetf(ios_base::skipws);
	InputFile2.unsetf(ios_base::skipws);

	while(InputFile >> myChar)
	{
		//cout << myChar << endl;
		if(isalpha(myChar))
		{
		    line += tolower(myChar);
		    continue;
		}
		if(isdigit(myChar))
		{
			line += myChar;
			continue;
		}
		if(line.size() != 0)	//if line is empty, which is the current char not an alpha or digit, continue.
		{
			myTokens[line] = 1;
			line = "";
		}
	}
	InputFile.close();
	//in this state myToken contain all token from file 1

	//Processing to find intersection:
	ofstream OutputFile;
	int size = myTokens.size();
	bool istooBig = false;
	if(size > 30) istooBig = true;

	if(istooBig)
	{
		cout << "Too many Unique Tokens, writing them in the output file!" << endl;
		OutputFile.open("outputCommonWords.txt");
	}

	while(InputFile2 >> myChar)
	{
		//cout << myChar << endl;
		if(isalpha(myChar))
		{
		    line += tolower(myChar);
		    continue;
		}
		if(isdigit(myChar))
		{
			line += myChar;
			continue;
		}
		if(line.size() != 0)	//if line is empty, which is the current char not an alpha or digit, continue.
		{
			if(myTokens[line] == 1) //if its 1 then, there is an intersection
			{
				myTokens[line] = 2;	//change the value into 2
				if(istooBig)
				{
					OutputFile << line << endl;
				}
				else
				{
					cout << line << endl;
				}
				//increment count;
				count++;
			}
			line = "";
		}
	}
	InputFile2.close();	

	//cout << "Number of Intersections : " << count << endl;
	if(istooBig)
	{
		OutputFile.close();
	}

	return count;
}

//Program Driver:
int main (int argc, char *argv[] )
{
	//read from command line:
	for(int i = 0;i<argc;i++)
	{
		cout << "argv[" << i << "] = "<<argv[i] << endl;
	}

	//check the arguments and run the program:
	if(argc >= 3)
	{
		cout << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" << endl;

		clock_t beginfindIntersection = clock();
		int numberofCommonWords = findIntersection(argv[1],argv[2]);
		clock_t endfindIntersection = clock();

		cout << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" << endl;
		cout << "Number of Common Words = " << numberofCommonWords << endl;

		double timetofindIntersection = double(endfindIntersection - beginfindIntersection) / CLOCKS_PER_SEC;
		cout << "Time to findIntersection = " << timetofindIntersection << "s" << endl;

	}
	else
	{
		cout << "Missing some parameters!" << endl;
	}

	return 0;
}