
# Shifting Bottleneck Heuristic with Earliest Due Date  - En erken teslim tarihi dispatching rule u kullanan Shifting Bottleneck Heuristic


import networkx as nx
import numpy as np

#gerekli modüller import edilir. networkx modülüyle problemimiz network problemine dönüştürülerek çözülür.



# Not : Classların içindeki commentler classların işlevini açıklamaktadır.


class Job(object):
    #job class ı operasyonların class ını temsil eder.
    #problemi networke aktarmak amacıyla işler aşağıda görüldüğü gibi çift olarak tanımlanır.
    def __init__(self, id, r, pt, d):
          self.id = id #iş çiftlerinin idleri (öncül,ardıl)
          self.r = r # işlerin yapıldıkları makineler (öncül işin makinesi,ardıl işin makinesi)
          self.pt = pt # işlerin belirtilen makinelerdeki processing time ları (öncül işin makinesindeki işlem süresi ,ardıl işin makinesindeki işlem süresi)
          self.d  = d # iş çiftlerinin son teslim tarihleri (ASCP den verilen)

class Jobshop(nx.DiGraph):

    #Jobshop classı job classını kullanarak programa tanıttığımız işleri network problemine dönüştürür.
    #Her iş bir node a dönüştürülür. Bu işlerin yapıldıkları makineler ve teslim tarihleri nodeların attribute u olarak bu classta tanımlanır.
    #İşlerin süreleri ise arc lara dönüştürülür.
    # U ve V adında source ve sink node u da eklenerek problem network problemine dönüştürülmüş olur.
    # Yukarıdaki maddeleri sağlayan fonksiyonları aşağıda inceleyebilirsiniz.


    def __init__(self): #, jobs):
        super().__init__()
        self.machines = {}
        self.add_node("U" , p=0)
        self.add_node("V" , p=0)



    def handleJobRoutings(self, jobs):
        for j in jobs.values():
            if j.id[0] == 'miss':
                self.add_edge("U", (j.r[1], j.id[1]))
            elif j.id[1] =='miss':
                self.add_edge((j.r[0], j.id[0]), "V")
            else:
                self.add_edge((j.r[0],j.id[0]),(j.r[1],j.id[1]))

    def handleJobProcessingTimes(self, jobs):
        for j in jobs.values():
            if j.id[0] != 'miss':
                self.add_node((j.r[0], j.id[0]), p=j.pt[0], d=j.d[0])


    def addJobs(self, jobs):

        self.handleJobRoutings(jobs)
        self.handleJobProcessingTimes(jobs)
        self.makeMachineSubgraphs()

    def makeMachineSubgraphs(self):
        machineIds = set(ij[0] for ij in self if ij[0] not in ("U", "V"))
        for m in machineIds:
            self.machines[m] = self.subgraph(ij for ij in self if ij[0] == m)

    def output(self):
        for m in sorted(self.machines):
            for j in sorted(self.machines[m]):
                print("{}: {}".format(j, self.node[j]['C']))

class CPM(nx.DiGraph):

    #CPM class ı bir networkteki critical path i bulduktan sonra node ların en erken başlanma ve en geç bitiş tarihleri gibi
    #attribute larını güncelleyen classtır.
    # earliest start tarihlerini bulurken forward method latest start ve finish tarihlerini kullanırken ise bakward methodunu kullanır.
    # İlgili fonksiyonları aşağıda görülebilir.

    def __init__(self):
        super().__init__()
        self._dirty = True
        self._makespan = -1
        self._criticalPath = None

    def add_node(self, *args, **kwargs):
        self._dirty = True
        super().add_node(*args, **kwargs)

    def add_nodes_from(self, *args, **kwargs):
        self._dirty = True
        super().add_nodes_from(*args, **kwargs)

    def add_edge(self, *args):  # , **kwargs):
        self._dirty = True
        super().add_edge(*args)  # , **kwargs)

    def add_edges_from(self, *args, **kwargs):
        self._dirty = True
        super().add_edges_from(*args, **kwargs)

    def remove_node(self, *args, **kwargs):
        self._dirty = True
        super().remove_node(*args, **kwargs)

    def remove_nodes_from(self, *args, **kwargs):
        self._dirty = True
        super().remove_nodes_from(*args, **kwargs)

    def remove_edge(self, *args):  # , **kwargs):
        self._dirty = True
        super().remove_edge(*args)  # , **kwargs)

    def remove_edges_from(self, *args, **kwargs):
        self._dirty = True
        super().remove_edges_from(*args, **kwargs)

    def _forward(self):
        for n in nx.topological_sort(self):
            S = max([self.node[j]['C']
                     for j in self.predecessors(n)], default=0)
            self.add_node(n, S=S, C=S + self.node[n]['p'])

    def _backward(self):
        for n in  list(reversed(list(nx.topological_sort(self)))):
            Cp = min([self.node[j]['Sp']
                      for j in self.successors(n)], default=self._makespan)
            self.add_node(n, Sp=Cp - self.node[n]['p'], Cp=Cp)

    def _computeCriticalPath(self):
        G = set()
        for n in self:
            if self.node[n]['C'] == self.node[n]['Cp']:
                G.add(n)
        self._criticalPath = self.subgraph(G)

    @property
    def makespan(self):
        if self._dirty:
            self._update()
        return self._makespan

    @property
    def criticalPath(self):
        if self._dirty:
            self._update()
        return self._criticalPath

    def _update(self):
        self._forward()
        self._makespan = max(nx.get_node_attributes(self, 'C').values())
        self._backward()
        self._computeCriticalPath()
        self._dirty = False

class Shift(Jobshop, CPM):

    #Shift classı bir network ve onun critical path ini girdi olarak alarak networkun makespan ini bulur.
    #Bunu yaparken ise tüm makinelerde işlenen işlerin bilgilerini ekrana basar.

    def output(self):
        print("makespan: ", self.makespan)
        for i in self.machines:
            print("Machine: " + str(i))
            s = "{0:<7s}".format("jobs:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += str("{0:>5d}".format(ij[1]))+"       "
            print(s)
            s = "{0:<7s}".format("p:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += str("{0:>.2f}".format(self.node[ij]['p']))+"          "
            print(s)
            s = "{0:<7s}".format("r:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += str("{0:>.2f}".format(self.node[ij]['S']))+"          "
            print(s)
            s = "{0:<7s}".format("d:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += str("{0:>.2f}".format(self.node[ij]['Cp']))+"      "
            print(s)
            s = "{0:<7s}".format("e:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += str("{0:>.2f}".format(self.node[ij]['p']+self.node[ij]['S']))+ "          "
            print(s)
            print("\n")

def argmin_kv(d):
    return min(d.items(), key=lambda x: x[1])

def argmax_kv(d):
    a = sorted(d, key=lambda x: x[1], reverse=True)
    return a[0]


# EDD_sequence ve find_edd fonksiyonları birlikte çalışır.
def EDD_sequence(d):
    # bir makinedeki işlenecek işleri EDD'ye göre sıralar.
    return sorted(d, key=lambda x : x [2])

def find_edd(mac):
    # Verilen bir makinenin EDD sequence ini bulur.
    jj = []
    seq = []
    for n in g.nodes:
            if n[0] == mac:
                a= (n[0], n[1], g.nodes[n]['d'])
                jj.append(a)
            seq1 = EDD_sequence(jj)
    for i in seq1:
        seq.append(i[:2])
    return seq


tardiness = []
chosen_machine = [] # çizelgelenen makineleri içerir.

def computeLmax(self): # Tüm makineleri EDD ye göre sıralar. En fazla toplam gecikmeye sebep olan makinenin çizelgelemesini EDD'ye göre döndürür.
    chosen_route =[]
    all_machines = []
    for m in self.machines:
        if m not in chosen_machine:
            seq = (find_edd(m))
            release = [self.node[j]['S'] for j in seq]
            finish = [0]*len(release)
            dd =  [self.node[j]['d'] for j in seq]
            for i, j in enumerate(seq):
                finish[i] = max(finish[i-1], release[i]) +self.node[j]['p']
            late = [f-d for d,f in zip(dd,finish)]
            late1 = []
            for i in late:
                if i >0:
                    late1.append(i)
            dd = sum(late1)
            s = seq
            all_machines.append((m, dd, s))
    chosen_machine.append(argmax_kv(all_machines)[0])
    chosen_route.append(argmax_kv(all_machines)[2])

    return (chosen_route[0])



def add_edges(self,nodes):
    #çizelgelemesi yapılan makinenin sıralamasını networke ekler.
    for i in range(0,len(nodes)-1):
        self.add_edge(nodes[i],nodes[i+1])
        if (nodes[i+1],nodes[i]) in self.edges:
            self.remove_edge(nodes[i+1],nodes[i])





j = {} # operasyonları barındıran tuple

#operasyonlar job classında belirtildiği gibi tanımlanır.
j[1]=Job([2379110,2379200],[12,12],[24,24],[-53.25])
j[2]=Job([2379200,2379250],[12,29],[24,2],[-29.25])
j[3]=Job([2379250,2379300],[29,47],[2,1.75],[-27.25])
j[4]=Job([2379300,2379400],[47,43],[1.75,0.5],[-25.5])
j[5]=Job([2379400,2379450],[43,12],[0.5,1],[-25])
j[6]=Job([2379450,2379605],[12,12],[1,24],[-24])
j[7]=Job([2379605,'miss'],[12,'miss'],[24,'miss'],[0])
j[8]=Job([307150,3071150],[8,33],[58,16],[-320])
j[9]=Job([3071150,3071400],[33,38],[16,14],[-304])
j[10]=Job([3071400,3071425],[38,48],[14,60],[-290])
j[11]=Job([3071425,3071500],[48,44],[60,12],[-230])
j[12]=Job([3071500,3071600],[44,36],[12,12],[-218])
j[13]=Job([3071600,30711150],[36,23],[12,8],[-206])
j[14]=Job([30711150,30711200],[23,11],[8,2],[-198])
j[15]=Job([30711200,30711250],[11,11],[2,4],[-196])
j[16]=Job([30711250,30711250],[11,12],[4,192],[-192])
j[17]=Job([30711250,'miss'],[12,'miss'],[192,'miss'],[0])
j[18]=Job([308050,3080150],[8,33],[14.5,4],[-80])
j[19]=Job([3080150,3080400],[33,38],[4,3.5],[-76])
j[20]=Job([3080400,3080425],[38,48],[3.5,15],[-72.5])
j[21]=Job([3080425,3080500],[48,44],[15,3],[-57.5])
j[22]=Job([3080500,3080600],[44,36],[3,3],[-54.5])
j[23]=Job([3080600,30801150],[36,23],[3,2],[-51.5])
j[24]=Job([30801150,30801200],[23,11],[2,0.5],[-49.5])
j[25]=Job([30801200,30801250],[11,11],[0.5,1],[-49])





# g jobshopu yaratılarak j tuple ındaki işler eklenir. Bu sayede problem network problemine dönüştürülmüş olunur.
g = Shift()
g.addJobs(j)

#Her iterasyonda bir makine çizelgelenerek güncellenen iş başlangıç ve bitiş tarihleri ekrana basılır.
for m in g.machines:
        print("iteration "+"{}".format(m))
        g.output() # çizelgelenen makineler networke eklendikten sonra iş başlangıç ve bitiş tarihlerini, buna bağlı olarak da critical path i günceller.
        print("\n")
        add_edges(g,computeLmax(g)) # çizelgelenen makinenin arclarını networke ekler.

g.output() # tüm iterasyonlar bittikten sonra network son hali için güncellenir.

print('\nFinal Makespan is ', g.makespan) # networkun makespanini ekrana basmak için g.makespan fonksiyonu çağrılır.

















