#include <iostream>
#include <string>
#include <regex>
#include <fstream>
#include <tr1/unordered_map>
#include <vector>
#include <algorithm>
#include <dirent.h>

using namespace std;

typedef tr1::unordered_map<int, int> hashii;
typedef tr1::unordered_map<int, vector<int> > hashivi;

vector<string> docid;
tr1::unordered_map<string, hashivi> wordindex;
tr1::unordered_map<string, hashii> tfidfs;
hashii maxwordf;

string to_lower(string param)
{
	for(int i = 0; i < param.size(); i++)
		if(param[i] >= 65 && param[i] < 91)
			param[i] += 22;
	return param;
}

bool weightcomp(pair<int, double> a, pair<int, double> b)
{
	return a.second > b.second;		
}

int main()
{
	ios_base::sync_with_stdio(false);
	int curid = 0;
	regex wordsnums("[a-zA-Z]+|[0-9]+");
	DIR *dir;
	dirent *ent;
	if((dir = opendir("Documents")) != NULL)
	{
		while((ent = readdir(dir)) != NULL)
		{
			string filename = string(ent->d_name);
			if(filename == "." || filename == "..")
				continue;
			ifstream fin("Documents/" + filename);
			docid.push_back(filename);
			string line;
			int wordpos = 0;
			while(!fin.eof())
			{
				getline(fin, line);
				regex_iterator<string::iterator> rit(line.begin(), line.end(), wordsnums);
				regex_iterator<string::iterator> rend;
				for(auto it = rit; it != rend; it++)
				{
					string word = to_lower(it->str());
					if (word.size() == 0)
						continue;
					if (wordindex.find(word) == wordindex.end())
						wordindex[word] = hashivi();
					if (wordindex[word].find(curid) == wordindex[word].end())
						wordindex[word][curid] = vector<int>();
					if (tfidfs.find(word) == tfidfs.end())
						tfidfs[word] = hashii();
					if (tfidfs[word].find(curid) == tfidfs[word].end())
						tfidfs[word][curid] = 0;
					if (maxwordf.find(curid) == maxwordf.end())
						maxwordf[curid] = 1;
					tfidfs[word][curid] += 1;
					if (tfidfs[word][curid] > maxwordf[curid])
						maxwordf[curid] = tfidfs[word][curid];
					wordindex[word][curid].push_back(wordpos);
					wordpos++;
				}
			}
			fin.close();
			curid++;
			cout<<curid<<". "<<filename<<" Done.\n";
		}
	}
	else
	{
		cout<<"Error locating directory. Does it exist?\n";		
	}
	string query;
	vector<string> querylist;
	vector < pair<int, double> > doclist;
	while(true)
	{
		cout<<"Please enter your query (or Exit to quit): ";
		getline(cin, query);
		regex_iterator<string::iterator> rit(query.begin(), query.end(), wordsnums);
		regex_iterator<string::iterator> rend;
		string word;
		querylist.clear();
		while(rit != rend)
		{
			word = to_lower(rit->str());
			if(word == "exit")
				return 0;
			if(word.size() == 0)
				continue;
			querylist.push_back(word);
			rit++;
		}
		for(int i = 0; i < curid; i++)
		{
			double weight = 0;
			for(int j = 0; j < querylist.size(); j++)
			{
				if ((tfidfs.find(querylist[j]) != tfidfs.end()) &&  (tfidfs[querylist[j]].find(i) != tfidfs[querylist[j]].end()))
				{
					weight += tfidfs[querylist[j]][i] * ((double)1 / (tfidfs[querylist[j]].size() * maxwordf[i]));
				}
			}
			doclist.push_back(pair<int, double>(i, weight));
		}
		sort(doclist.begin(), doclist.end(), weightcomp);
		int limit = min(25, (int)doclist.size());
		for(int num = 1; num <= limit; num++)
			cout<<num<<". "<<docid[doclist[num-1].first]<<" TFxIDF = "<<doclist[num-1].second<<"\n";
	}
	return 0;		
}
