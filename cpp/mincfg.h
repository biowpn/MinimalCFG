
#include <vector>
#include <set>
#include <string>

// #include <iostream>

struct rule_t
{
    int nt{0};
    int t_left{0};
    int t_right{0};
};

bool is_match(const std::string &str, std::vector<rule_t> rules)
{
    auto n = str.length();
    if (n < 2)
    {
        return false;
    }

    std::vector<std::vector<std::set<int>>> M;
    M.resize(n);
    for (auto &row : M)
    {
        row.resize(n);
    }

    for (std::size_t i = 0; i < n; ++i)
    {
        M[i][i].insert(str[i]);
    }

    for (std::size_t s = 1; s < n; ++s)
    {
        for (std::size_t i = 0; i < n - s; ++i)
        {
            for (std::size_t k = i; k < i + s; ++k)
            {
                for (const auto &rule : rules)
                {
                    if (M[i][k].find(rule.t_left) != M[i][k].end() && M[k + 1][i + s].find(rule.t_right) != M[k + 1][i + s].end())
                    {
                        M[i][i + s].insert(rule.nt);
                    }
                }
            }
        }
    }

    // for (std::size_t i = 0; i < n; ++i)
    // {
    //     for (std::size_t j = 0; j < n; ++j)
    //     {
    //         printf("M[%d][%d] = {", i, j);
    //         for (const auto &e : M[i][j])
    //         {
    //             std::cout << e << ", ";
    //         }
    //         std::cout << "}" << std::endl;
    //     }
    // }

    return M[0][n - 1].find(-1) != M[0][n - 1].end();
}
