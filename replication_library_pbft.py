from queue import Queue
import threading
import time
import random
import hashlib

MIN_DELAY = 1
MAX_DELAY = 10
TIMEOUT = 9
NO_OF_REPLICAS = 10


class Environment :

    def __init__(self,view,primary,f_nodes,total_nodes):
        self.view = view
        self.primary = primary
        self.f_nodes = f_nodes
        self.total_nodes = total_nodes


class Client :

    def __init__(self,id,primary,list_of_replicas,view_number):
        self.id = id
        self.queue = Queue() 
        self.primary = primary
        self.list_of_replicas = list_of_replicas
        self.view_number = view_number

    def request(self,user_input1,user_input2):
        # TO-DO : Client Request to Primary
        delay = self.get_delay()
        time.sleep(delay)
        if delay < 90 :
            self.primary.queue.put([self,user_input1,user_input2])
        time.sleep(120)
        if self.queue.empty() :
            print('Client --- No Reply from Primary')
            print('Client --- Initiating multicast to clients')
            for replica in self.list_of_replicas :
                delay = self.get_delay()
                time.sleep(delay)
                if delay < 90 :
                    replica.queue.put([user_input1,user_input2])
        else :
            message_received = self.queue.get()
            if type(message_received) == type(0) :
                print('Result of %d + %d = %d'%(user_input1,user_input2,message_received))     
            else :
                print('Client --- View Change Message is received')
                self.primary = message_received[0]
                self.list_of_replicas = message_received[1]
                self.view_number = message_received[2]
                print('Client --- View Changed, sending request again')
                self.request(user_input1,user_input2)


    def get_delay(self):
        # TO-DO : Generates random delay between 1-100 seconds
        return random.randint(1,10)

class Primary :

    def __init__(self,id,sequence_number,view_number,list_of_replicas):
        self.queue = Queue()
        self.id = id
        self.sequence_number = sequence_number
        self.view_number = view_number
        self.list_of_replicas = list_of_replicas

    def pre_prepare_request(self):
        # TO-DO : Multicast Pre Prepare Request to Replicas

        while True :

            if self.queue.empty() :
                pass

            else :
                message_received = self.queue.get()
                digest = self.get_hash(message_received)
                print('Primary --- Message received from client : ',message_received)

                for replica in self.list_of_replicas :
                    delay = self.get_delay()
                    time.sleep(delay)
                    if delay < 90 :
                        replica.queue.put(['PRE_PREPARE',self.view_number,self.sequence_number,digest,message_received])

        
    
    def get_delay(self):
        # TO-DO : Generates random delay between 1-100 seconds
        return random.randint(1,10)
    
    def get_hash(self,message):
        message = str(message)
        h = hashlib.sha256()
        h.update(message.encode())
        return h.hexdigest()

class Replica :

    def __init__(self,state,id,view_number):
        self.queue = Queue()
        self.id = id
        self.view_number = view_number
        self.state = state

    def verify_pre_prepare(self):
        # TO-DO : Verify Pre Prepare Requests from Primar
        pass
    
    def prepare_request(self,view_number,sequence_number,digest,list_of_replicas):
        # TO-DO : Send Prepare Request
        print('Replica %d ---- Sending PREPARE REQUEST to other replicas'%(self.id))
        for i in range(9):
            if self.id != i :
                list_of_replicas[i].queue.put(['PREPARE',view_number,sequence_number,digest,self.id])

    def is_prepared(self):
        # TO-DO : P-Certificate
        pass
    
    def commit_request(self,view_number,sequence_number,digest,list_of_replicas):
        # TO-DO : Commit Request
        print('Replica %d ---- Sending COMMIT REQUEST to other replicas'%(self.id))
        for i in range(9):
            if self.id != i :
                list_of_replicas[i].queue.put(['COMMIT',view_number,sequence_number,digest,self.id])

    
    def reply(self,message,view_number):
        # TO-DO : Send Reply to Client
        print('Message at Replica ',self.id,' : ',message)
        message[0].queue.put(message[1]+message[2])
        

    def view_change(self):
        # TO-DO : Send Reply to Client
        pass

    def get_delay(self):
        # TO-DO : Generates random delay between 1-100 seconds
        return random.randint(1,10)

def client_thread(client):
    # TO-DO : Modelling Client Behavior
    client.request(5,8)
    pass

def primary_thread(primary):
    # TO-DO : Modelling Primary Behavior
    primary.pre_prepare_request()
    pass

def replica_thread(replica,list_of_replicas):
    # TO-DO : Modelling Replica Behavior
    #time.sleep(replica.get_delay())
    prepare_requests = []
    commit_requests = []
    prepared = False
    commit = False
    view_number = 0
    sequence_number = 0
    digest = 0
    message = 0
    while True :
        
        if replica.queue.empty():
            continue
        else :       
            val = replica.queue.get()
            if replica.state == 'PRE_PREPARE' and val[0] == 'PRE_PREPARE' :
                print('Value of val at Replica ',replica.id,' : ',val)
                replica.prepare_request(val[1],val[2],val[3],list_of_replicas)
                view_number = val[1]
                sequence_number = val[2]
                digest = val[3]
                message = val[4]
                replica.state = 'PREPARE'

            else :
                if val[0] == 'PREPARE':
                    prepare_requests.append(val)
                if val[0] == 'COMMIT':
                    commit_requests.append(val)    

            if len(prepare_requests) > 5 :
                prepared = True
                print('Replica %d --- Prepared'%(replica.id))
                prepare_requests = []
                
            
            if len(commit_requests) > 5 :
                commit = True
                print('Replica %d --- Committed'%(replica.id))
                commit_requests = []

            if prepared and replica.state == 'PREPARE' :
                replica.commit_request(view_number,sequence_number,digest,list_of_replicas)
                prepared = False
                replica.state = 'COMMIT'

            if commit and replica.state == 'COMMIT':
                print('At Replica ',replica.id,' val[4] : ',val[4])
                replica.reply(message,view_number)
                commit = False



if __name__ == '__main__' :

    list_of_replicas = []
    for i in range(2,11) :
        r = Replica('PRE_PREPARE',i,0)
        list_of_replicas.append(r)
    primary = Primary(1,1,0,list_of_replicas)
    client = Client(0,primary,list_of_replicas,0)
    client_model = threading.Thread(target=client_thread,args=(client,))
    primary_model = threading.Thread(target=primary_thread,args=(primary,))
    list_of_replica_model = []
    for i in range(9):
        replica_model = threading.Thread(target=replica_thread,args=(list_of_replicas[i],list_of_replicas))
        list_of_replica_model.append(replica_model)
    
    for i in range(9):
        list_of_replica_model[i].start()
    primary_model.start()
    client_model.start()
    client_model.join()

    
    

    