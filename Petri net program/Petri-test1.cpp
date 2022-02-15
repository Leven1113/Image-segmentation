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
// ��Ȩ�ı�
class Edge {
public:
    Edge(int v, int weight) : v(v), weight(weight) {}
    // ����Ľڵ�
    int v;
    // �ߵ�Ȩ��
    int weight;
};
// ��Ȩ�����޻�ͼ
class Graph {
public:
    Graph(int V);
    ~Graph();
    void AddDirectEdge(int v, int w, int weight);
	int  Value(int v, int w);
    // ��Ա����
    int     V;
    int     E;
    list<Edge> *adj;     // �ڽӱ��ʾ
};
// ·����Ȩֵ
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
    // �ҵ�����֮������·��
    void Traversal(int v, int w);
    // �������·���ĳ���
    int  Compute(list<int> &list);
    // ����ƽ��·���ĳ���
	int  Compute1(list<int> &list);
    // �ҳ����·��
    void SelectPath();
    // ��ӡ���·��
    void PrintPath();
    // ��ӡ·���ڵ�
    static void PrintList(list<int> &list);
    // ��Ա����
    int   *marked;
    bool  *stacked;
    Graph *graph;
    // ���·�������ȼ�����
    priority_queue<Path> pq;
    // ������·����vector
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
    int       node = v;             // ��ǰ�ڵ�
    int       value;
    list<int> stack;
    if (graph->E == 0) return;

    stacked[node] = true;
    stack.push_back(node);
    while (!stack.empty()) {
        node = *stack.rbegin();
        if (node == w) {
            // �ҵ����սڵ�
            // �˴���¼·��������·������
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

// �ҵ�һ�����ڵĽڵ�
int DFS::Neighbour(int v)
{
    for (list<Edge>::iterator iter = graph->adj[v].begin();
         iter != graph->adj[v].end();
         ++iter) {
        if (stacked[iter->v] == false) {
            if (marked[v] == -1) {
                // ����һ������ջ�ڵĽڵ�
                for (; (iter != graph->adj[v].end()) && stacked[iter->v] == true; ++iter);
                if (iter == graph->adj[v].end()) return -1;
                else                             return iter->v;
            } else if (marked[v] == iter->v) {
                // �����ڽӱ�����ʣ�����һ���ҵ��ĵط��ٴ�Ѱ��
                ++iter;
                // ����һ������ջ�ڵĽڵ�
                for (; (iter != graph->adj[v].end()) && stacked[iter->v] == true; ++iter);
                if (iter == graph->adj[v].end()) return -1;
                else                             return iter->v;
            }
            // else ���else���Թ�֮ǰ�ҵ�����Щ�ڵ㣬ֱ���ҵ���һ���ҵĽڵ�
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
        cout << "����>" <<*iter ;
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
        // ��֤
       // cout << "���·��֮һ value�� " << p.value <<",    ";
        cout << "���·��֮һ" << ",";
		cout<<"·��Ϊ��";
       PrintList(p.path);
        // ����vector
        vec.push_back(p);
        pq.pop();
    }
}
// ���������ŵļ���
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
    // ����
    if (vec.size() <= 0) {
        cout << "Internal Error!" << endl;
        return;
    }
    // ����һ�����·��
    if (vec.size() == 1) {
        cout << "���·��Ϊ: ";
        PrintList(vec[0].path);	
        cout << endl;
        return;
    }
	cout << "�ж������·��!" << endl;
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
			//cout << "��" << max[0] << "��" << endl;
			cout << "·��Ϊ��" << endl; 
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
			// �Ƚ�·������
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
							cout << "��������(��0��ʼ)��";
							cin >> r;
						} while(r >= oldvec.size());

						cout << "ѡ���·��Ϊ: ";
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
		cout << "�ļ���ȡʧ�ܣ�" << endl;
		exit(1);
	}
    in >> V;
	cout << "�ڵ����Ϊ��" << V << endl;
    Graph graph(V);
    DFS dfs(&graph);
    // ��
    int start, end, value;

    do {
        cout.flush();
        // ��ȡ
        in >> start;
        if (start == -1) break;
        in >> end >> value;
        // ��ӽڵ�
        graph.AddDirectEdge(start, end, value);
    } while (1);
	srand(time(NULL));
    // ����·��
    cout << "�����뿪ʼ��������� (start end): " << endl;
    cin >> start >> end;
    dfs.Traversal(start, end);
    dfs.SelectPath();
    // ���·����ѡ�������������
    dfs.PrintPath();
    return 0;
}
