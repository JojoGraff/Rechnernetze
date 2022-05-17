
import heapq as hq

print("Hello World")

#Methode start() ##startet sim


heap = []

for i in range(10):
    heap.append(i)
    print(heap)
hq.heapify(heap)
print(heap)
#Kl     Ereignisliste
#   KV:     Heap-Queue: Simulationszeit und die Ereignisnummer
#   KM:     event=pop(), push(event) und start()
#

#KL:    Station

#Heap-Queue: z.B (1,2,3,4,5)    Ereigniszeitpunkt, Ereignispriorität,
#                               Ereignisnummer,  Ereignisfunktion
#                               und optional den Ereignisargumenten

#KL:    KundeIN
#       Konstrukter --> 3Tupel (zu besuchende Stationen)
#       L2=list(L1)






