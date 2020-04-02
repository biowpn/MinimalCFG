
#include <cstring>
#include <iostream>
#include <fstream>
#include <sstream>
#include <streambuf>

#include "mincfg.h"

std::istream *open_file(const char *path)
{
    if (std::strcmp(path, "-") == 0)
    {
        return &std::cin;
    }
    auto ifs = new std::ifstream(path);
    if (!ifs->good())
    {
        std::cout << "bad file: " << path << std::endl;
        delete ifs;
        return nullptr;
    }
    return ifs;
}

int main(int argc, char **argv)
{
    if (argc < 3)
    {
        std::cout << "usage: <grammar-file> <string-file>" << std::endl;
        return 0;
    }

    auto ifs1 = open_file(argv[1]);
    if (ifs1 == nullptr)
    {
        return -1;
    }

    auto ifs2 = open_file(argv[2]);
    if (ifs2 == nullptr)
    {
        return -1;
    }

    std::vector<rule_t> rules;
    while (!ifs1->eof())
    {
        rule_t rule;
        *ifs1 >> rule.nt;
        *ifs1 >> rule.t_left;
        *ifs1 >> rule.t_right;
        if (rule.nt && rule.t_left && rule.t_right)
        {
            rules.emplace_back(rule);
        }
    }

    std::stringstream ss;
    ss << ifs2->rdbuf();

    std::cout << (is_match(ss.str(), rules) ? "Yes" : "No") << std::endl;

    return 0;
}
