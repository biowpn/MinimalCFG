
#include <iostream>
#include <fstream>

#include "mincfg.h"

int main(int argc, char **argv)
{

    if (argc < 3)
    {
        std::cout << "usage: <grammar file> string" << std::endl;
        return 0;
    }

    std::ifstream ifs(argv[1]);
    if (!ifs.good())
    {
        std::cout << "bad file: " << argv[1] << std::endl;
        return -1;
    }

    std::vector<rule_t> rules;
    while (!ifs.eof())
    {
        rule_t rule;
        ifs >> rule.nt;
        ifs >> rule.t_left;
        ifs >> rule.t_right;
        if (rule.nt && rule.t_left && rule.t_right)
        {
            rules.emplace_back(rule);
        }
    }

    std::cout << (is_match(argv[2], rules) ? "yes" : "no") << std::endl;

    return 0;
}
