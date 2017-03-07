/** 
file name: assignment1_PartB.cpp
Author: Kevin Permana
UCInet ID: 50259184
CS121 HW 1 part A
*/
#include <iostream>
#include <map>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <cstring>
#include <string>
#include <typeinfo>
#include <ctime>
#include <stdio.h>

using namespace std;

typedef vector<const __cxx11::basic_string<char>*> myAdressofString;
typedef unordered_map<string,int> myMap;
typedef map<int, myAdressofString, greater<int>> myOrderedMap;

/** tokenize
	reads in a text file and returns a list of the tokens in that file
    @param TextFilePath, string of text file path
    @param myTokens, result after tokenize
*/
void tokenize(string TextFilePath, myMap &myTokens)
{
	ifstream InputFile;
	InputFile.open(TextFilePath);
	if(!InputFile)
    {
    	cout << "File not found! : " << TextFilePath << endl;
        exit(1);
    } 
	
	char myChar;
	string line = "";
	InputFile.unsetf(ios_base::skipws);
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
			myTokens[line]++;
			line = "";
		}
	}

	InputFile.close();
	return;
}

/** computeWordFrequencies
	this function will count the number of occurrences of each word in the token list.
    @param TextFilePath, string of text file path
    @param myTokens, result after tokenize
*/
void computeWordFrequencies(myMap &myTokens)
{
	//cout <<"already in tokenize"<<endl;
	return;
}

/** printThis
	will prints out the word frequency counts onto the screen. The print out should be ordered by decreasing frequency. (so, highest frequency words first)
    @param myTokens map with unique tokens in it
*/
void printThis(myMap &myTokens)
{
	int size = myTokens.size();

	myOrderedMap myOrderedTokens;

	for (auto& mypair : myTokens) 
	{
		myOrderedTokens[mypair.second].push_back(&mypair.first);

		/* //old code: use find to iterate of myTokens, more control but [] is faster.
		myIterator = myOrderedTokens.find(mypair.second);
  		if (myIterator != myOrderedTokens.end())
		{
			myOrderedTokens.insert(myOrderedMap::value_type(mypair.second, myAdressofString()));
			myOrderedTokens[mypair.second].push_back(&mypair.first);
		}
		else
		{
			myOrderedTokens[mypair.second].push_back(&mypair.first);
		}
		*/
		//cout << mypair.first << ": " << mypair.second << endl;
	}


	//int size2 = myOrderedTokens.size();
	//cout << "Total of Unique Word Frecuencies = " << size2 << endl;
	cout << "Frequencies : Words "<< endl;

	int count = 0;
	myOrderedMap::iterator myIterator;
	for (myIterator = myOrderedTokens.begin(); myIterator != myOrderedTokens.end(); myIterator++)
	{
	    cout << myIterator->first << " : ";
	    for (auto value: myIterator->second)
	    {
  			cout << *value << ' ';
  			//count++;
	    }
  		cout << endl;
	}

	//cout << "Number of Unique Tokens = " << count << endl;
	
	return;
}


/** writeThis
	will write the word frequency counts onto an output file. The print out should be ordered by decreasing frequency. (so, highest frequency words first)
    @param myTokens map with unique tokens in it
*/
void writeThis(myMap &myTokens)
{	
	ofstream OutputFile;
	OutputFile.open("output.txt");	//output.txt the name of output file.

	int size = myTokens.size();

	//OutputFile << "Number of Unique Tokens = " << size << endl;

	myOrderedMap myOrderedTokens;

	for (auto& mypair : myTokens) 
	{		
		myOrderedTokens[mypair.second].push_back(&mypair.first);
	}

	OutputFile << "Frequencies : Words "<< endl;

	int count = 0;
	myOrderedMap::iterator myIterator;
	for (myIterator = myOrderedTokens.begin(); myIterator != myOrderedTokens.end(); myIterator++)
	{
	    OutputFile << myIterator->first << " : ";
	    for (auto value: myIterator->second)
	    {
  			//OutputFile << myIterator->first <<" : "<< *value << endl;
  			OutputFile << *value << ' ';
  			//count++;
	    }
  		OutputFile << endl;
	}

	OutputFile.close();

	cout << "Sucess!!" << endl;
	//OutputFile << "Number of Unique Tokens = " << count << endl;
	return;
}


//Program Driver:
int main (int argc, char *argv[] ) {

	myMap myTokens;
	int size = 0;

	for(int i = 0;i<argc;i++)
	{
		cout << "argv[" << i << "] = "<<argv[i] << endl;
	}
	
	if(argc>1)
	{
		clock_t beginTokenize = clock();
		tokenize(argv[1],myTokens);
		clock_t endTokenize = clock();

		// computeWordFrequencies(myTokens);
		
		size = myTokens.size();
		cout << "Number of Unique Tokens = " << size << endl;
		cout << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" << endl;
		
		clock_t beginPrinting = clock();
		if(size < 1000)
		{
			printThis(myTokens);
		}
		else
		{
			cout << "Too many Unique Tokens, writing them in the output file!" << endl;
			writeThis(myTokens);
		}
		clock_t endPrinting = clock();


		double timetoTokenize = double(endTokenize - beginTokenize) / CLOCKS_PER_SEC;
		double timetoPrint = double(endPrinting - beginPrinting) / CLOCKS_PER_SEC;
		
		cout << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" << endl;
		cout << "Time to Tokenize = " << timetoTokenize << "s" << endl;
		cout << "Time to Print    = " << timetoPrint << "s" << endl;

	}
	else
	{
		cout << "Missing some parameters!" << endl;
	}

	return 0;
}