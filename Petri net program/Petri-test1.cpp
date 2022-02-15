#include <iostream>
#include <algorithm>
#include <climits>
#include <cstdlib>
#include <ctime>
#include <cstdio>
#include <fstream>
#include <list>
#include <stack>
#include <queue>
#include <vector>
using namespace std;
// 带权的边
class Edge {
public:
    Edge(int v, int weight) : v(v), weight(weight) {}
    // 到达的节点
    int v;
    // 边的权重
    int weight;
};
// 带权有向无环图
class Graph {
public:
    Graph(int V);
    ~Graph();
    void AddDirectEdge(int v, int w, int weight);
	int  Value(int v, int w);
    // 成员变量
    int     V;
    int     E;
    list<Edge> *adj;     // 邻接表表示
};
// 路径和权值
class Path {
public:
    Path(list<int> &l, int value);
    list<int> path;
    int    value;
    bool operator< (const Path &p2) const;
};
class DFS {
public:
    DFS(Graph *graph);
    ~DFS();
    // 找到两点之间所有路径
    void Traversal(int v, int w);
    // 计算最短路径的长度
    int  Compute(list<int> &list);
    // 计算平均路径的长度
	int  Compute1(list<int> &list);
    // 找出最短路径
    void SelectPath();
    // 打印最短路径
    void PrintPath();
    // 打印路径节点
    static void PrintList(list<int> &list);
    // 成员变量
    int   *marked;
    bool  *stacked;
    Graph *graph;
    // 存放路径的优先级队列
    priority_queue<Path> pq;
    // 存放最短路径的vector
    vector<Path> vec;
private:
    int Neighbour(int v);
};
Graph::Graph(int V)
{
    this->V = V;
    this->E = 0;
    this->adj = new list<Edge>[V];
}
Graph::~Graph()
{
    delete[] this->adj;
}
void Graph::AddDirectEdge(int v, int w, int weight)
{
    this->adj[v].push_front(Edge(w, weight));
    this->E++;
}
int Graph::Value(int v, int w)
{
	for (list<Edge>::iterator iter = adj[v].begin();
		iter != adj[v].end();
		++iter) {
			if (iter->v == w) {
				return iter->weight;
			}
		}
		return -1;
}

Path::Path(list<int> &l, int value)
{
    for (list<int>::iterator iter = l.begin();
         iter != l.end();
         ++iter) {
        this->path.push_back(*iter);
    }
    this->value = value;
}
bool Path::operator<(const Path &p2) const
{
    return this->value > p2.value;
}
DFS::DFS(Graph *graph)
{
    this->graph = graph;
    this->marked = new int[graph->V];
    this->stacked = new bool[graph->V];
    for (int i = 0; i < graph->V; i++)
        this->marked[i] = -1;
    for (int j = 0; j < graph->V; j++)
        this->stacked[j] = false;
}
DFS::~DFS()
{
    delete[] this->marked;
    delete[] this->stacked;
}
void DFS::Traversal(int v, int w)
{
    int       node = v;             // 当前节点
    int       value;
    list<int> stack;
    if (graph->E == 0) return;

    stacked[node] = true;
    stack.push_back(node);
    while (!stack.empty()) {
        node = *stack.rbegin();
        if (node == w) {
            // 找到最终节点
            // 此处记录路径，计算路径长度
            value = Compute(stack);
            pq.push(Path(stack, value));
            stack.pop_back();
            stacked[node] = false;
            marked[node] = -1;
        } else {
            int temp = Neighbour(node);
            if (temp != -1) {
                marked[node] = temp;
                node = temp;
                stack.push_back(node);
                stacked[node] = true;
            } else {
                stack.pop_back();
                stacked[node] = false;
                marked[node] = -1;
            }
        }
    }
}

// 找第一个相邻的节点
int DFS::Neighbour(int v)
{
    for (list<Edge>::iterator iter = graph->adj[v].begin();
         iter != graph->adj[v].end();
         ++iter) {
        if (stacked[iter->v] == false) {
            if (marked[v] == -1) {
                // 找下一个不在栈内的节点
                for (; (iter != graph->adj[v].end()) && stacked[iter->v] == true; ++iter);
                if (iter == graph->adj[v].end()) return -1;
                else                             return iter->v;
            } else if (marked[v] == iter->v) {
                // 利用邻接表的性质，从上一次找到的地方再次寻找
                ++iter;
                // 找下一个不在栈内的节点
                for (; (iter != graph->adj[v].end()) && stacked[iter->v] == true; ++iter);
                if (iter == graph->adj[v].end()) return -1;
                else                             return iter->v;
            }
            // else 这个else会略过之前找到的那些节点，直到找到上一次找的节点
        }
    }
    return -1;
}
void DFS::PrintList(list<int> &l)
{
    cout << " ";
    for (list<int>::iterator iter = l.begin();
         iter != l.end();
         ++iter) {
        cout << "——>" <<*iter ;
    }
    cout << endl;
}
int DFS::Compute(list<int> &l)
{
    int value = 0;
    int t = 0;
    for (list<int>::iterator iter = l.begin();
         iter != l.end();) {
        int start, end;
        start = *iter;
        ++iter;
        end   = *iter;
        for (list<Edge>::iterator iter = graph->adj[start].begin();
             iter != graph->adj[start].end();
             ++iter) {
            if (iter->v == end) {
            	t++;
                value += iter->weight;
                break;
            }
        }
        for (list<Edge>::iterator iter = graph->adj[start].begin();
		             iter != graph->adj[start].end();
		             ++iter) {
		            if (iter->weight > value/t) {
		                value = value/t;
		            }
		            
		        }
    }
    return value; 
}
int DFS::Compute1(list<int> &l)
{
    int value = 0;
    int t=0;
    for (list<int>::iterator iter = l.begin();
         iter != l.end();) {
        int start, end;
        start = *iter;
        ++iter;
        end   = *iter;
        for (list<Edge>::iterator iter = graph->adj[start].begin();
             iter != graph->adj[start].end();
             ++iter) {
            if (iter->v == end) {
            	t++;
                value += iter->weight;
                break;
            }
        }
    }
    return value/t;
}
void DFS::SelectPath()
{
    int old = INT_MAX;
    while (!pq.empty()) {
        Path p = pq.top();
        if (p.value > old)
            break;
        old = p.value;
        // 验证
       // cout << "最短路径之一 value： " << p.value <<",    ";
        cout << "最短路径之一" << ",";
		cout<<"路径为：";
       PrintList(p.path);
        // 加入vector
        vec.push_back(p);
        pq.pop();
    }
}
// 返回最大序号的集合
vector<int> max_vec(vector<int> &vec)
{
	vector<int> seq;
	int max = 0;
	for (vector<int>::iterator iter = vec.begin();
		iter != vec.end();
		++iter) {
			
			if (*iter > max) {
				max = *iter;
			}
	}
	for (int i = 0; i < vec.size(); ++i) {
			if (vec[i] == max) {
				seq.push_back(i);
			}
	}
	return seq;
}
void DFS::PrintPath()
{
    int r;
    // 错误
    if (vec.size() <= 0) {
        cout << "Internal Error!" << endl;
        return;
    }
    // 仅有一条最短路径
    if (vec.size() == 1) {
        cout << "最短路径为: ";
        PrintList(vec[0].path);	
        cout << endl;
        return;
    }
	cout << "有多条最短路径!" << endl;
	vector<int> len;
	vector<int> max;
	vector<Path> oldvec;
	for (int i = 0; ; i++) {
		len.clear();
		for (int j = 0; j < vec.size(); j++) {
			list<int>::iterator iter = vec[j].path.begin();
			advance(iter, i);
			int t1 = *iter;
			iter++;
			int t2 = *iter;
			len.push_back(graph->Value(t1, t2));
		}
		max = max_vec(len);
		if (max.size() == 1) {
			//cout << "第" << max[0] << "条" << endl;
			cout << "路径为：" << endl; 
			PrintList(vec[max[0]].path);
			return;
		}
		if (max.size() > 1) {
			oldvec = vec;
			vec.clear();
			for (vector<int>::iterator iter = max.begin();
				iter != max.end();
				++iter) {
					vec.push_back(oldvec[*iter]);
			}
			// 比较路径长度
			int flag1 = 0;
			for (int k = 0; k < vec.size(); k++) {
				if (vec[k].path.size() > i + 2) {
					flag1 = 1;
					oldvec = vec;
					vec.clear();
					for (int abc = 0; abc < oldvec.size(); abc++) {
						vec.push_back(oldvec[abc]);
					}
				}
			}
			if (flag1 == 0) {
				oldvec = vec;
				vec.clear();
			}
			if (vec.size() == 0) {
					int lennnn = oldvec[0].path.size();
					int flag = 0;
					for (int l = 0; l < oldvec.size(); l++) {
						if (lennnn != oldvec[l].path.size()) {
							flag = 1;
						}
					}
					if (flag == 0) {
						for (int i = 0; i < oldvec.size(); i++) {
							PrintList(oldvec[i].path);
						}
						do {
							cout << "请输入编号(从0开始)：";
							cin >> r;
						} while(r >= oldvec.size());

						cout << "选择的路径为: ";
						PrintList(oldvec[r].path);
						cout << endl;
						return;
					}
			}
		}

	}

}
int main(void)
{
    int V;
	fstream in("file1.txt", ios::in);
	if (!in.good()) 
	{
		cout << "文件读取失败！" << endl;
		exit(1);
	}
    in >> V;
	cout << "节点个数为：" << V << endl;
    Graph graph(V);
    DFS dfs(&graph);
    // 边
    int start, end, value;

    do {
        cout.flush();
        // 读取
        in >> start;
        if (start == -1) break;
        in >> end >> value;
        // 添加节点
        graph.AddDirectEdge(start, end, value);
    } while (1);
	srand(time(NULL));
    // 遍历路径
    cout << "请输入开始点与结束点 (start end): " << endl;
    cin >> start >> end;
    dfs.Traversal(start, end);
    dfs.SelectPath();
    // 最短路径的选择在这个函数内
    dfs.PrintPath();
    return 0;
}
