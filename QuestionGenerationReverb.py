import re
from FullPipeline import *
from triple_frame import *

def ler_ficheiro_testes(file_name):
	#ler input
	frase = []
	entidade1 = []
	entidade2 = []
	relacao = []
	with open(file_name,"r") as f:
		for index,line in enumerate(f):
			if(line!="\n"):
				coisas = line.split("\t")
				frase_currente = []
				frase_currente.append(coisas[0].strip("\n"))
				frase.append(frase_currente)
				#frase_currente.append(coisas[2])
				#print(coisas[3])
				entidade1.append(coisas[1])

				frase_currente = []
				frase_currente.append(coisas[3].strip("\n"))
				relacao.append(frase_currente)

				#print(coisas[6])
				entidade2.append(coisas[4])
	for i in range(len(frase)):
		print("FRASE: " + str(frase[i])+"\n")
		teste_sent(frase[i],entidade1[i],entidade2[i],"")

def filter_amazon(tags,tokens):
	relacoes = []
	m = re.finditer('(( v-fin| v-ger| v-inf| v-pcp| v)( adv)?( art)?)(( n| adj| adv|( pron-det| pron-indp| pron-pers| propess| prosub)))*( prp|  art)|(( v-fin| v-ger| v-inf| v-pcp| v)( adv)?( art)?)( prp|  art)|( v-fin| v-ger| v-inf| v-pcp| v)( adv)?',tags)
	for match in m:
		s = match.start()
		e = match.end()
		tags_dividida_antes = len(tags[0:s].split(" "))
		tags_dividida_durante = len(tags[s:e].split(" ")) + tags_dividida_antes
		relacoes.append(tokens[tags_dividida_antes:tags_dividida_durante])
		#print(tokens[tags_dividida_antes:tags_dividida_durante])
	'''
	for line in m:
		print(line)
	'''
	return relacoes

def imprime_relacao(primeira_entidade,segunda_entidade,relacoes):
	entidade1 = primeira_entidade
	entidade2 = segunda_entidade
	'''
	for primeira_parte in primeira_entidade:
		entidade1+=primeira_parte+ " "

	for segunda_parte in segunda_entidade:
		entidade2+=segunda_parte+ " "
	'''
	for relacao in relacoes:
		#print(relacao)
		frase = ""
		frase+=entidade1
		for elem in relacao:
			frase+=elem+" "
		frase+=entidade2
		print(frase)

def imprime_relacao_2(primeira_entidade,segunda_entidade,relacoes):
	entidade1 = primeira_entidade
	entidade2 = segunda_entidade
	for relacao in relacoes:
		#print(relacao)
		frase = "("
		frase+=entidade1+","
		for elem in relacao:
			frase+=elem+" "
		frase+=","+entidade2 + ")"
		print(frase)

def metricas(obtido,esperado):
	esperado=esperado.split(" ")
	obtido = obtido
	print(obtido)
	print(esperado)
	tamanho_inicial_esperado =  len(esperado)
	tamanho_inicial_obtido =  len(obtido)
	valor_final = 0
	for token in obtido:
		if(token in esperado):
			esperado.remove(token)
			valor_final+=1
	print("Precisão:")
	prec = valor_final/tamanho_inicial_obtido
	print(str(prec))
	print("Abrangência:")
	abran = valor_final/tamanho_inicial_esperado
	print(str(abran))
	print("F-1:")
	if(prec == 0.0 or abran == 0.0):
		f1 = 0
	else:
		f1 = 2*(prec*abran)/(prec+abran)
	print(str(f1))
	return prec,abran,f1


def teste_sent_none(frase,out_file):
	relacao = frase.split("| ")[1].replace("\n","")
	frase_list = []
	frase_list.append(frase.split("| ")[0])
	frase = frase_list
	tags_sentence = ""
	tokens,tags,lemas,entidades,np = full_pipe(frase,"")
	print(tokens)
	#print(tags)
	for index,elem in enumerate(tags):
		tags_sentence += elem + " "
	relacoes = filter_amazon(tags_sentence,tokens)
	if(len(relacoes)>0):
	#print(relacoes,relacao)
		return metricas(relacoes[0],relacao)
	else:
		return 0,0,0
	#imprime_relacao_2("","",relacoes)

def teste_sent(frase,primeira_entidade,segunda_entidade,out_file):
	tags_sentence = ""
	tokens,tags,lemas,entidades,np = full_pipe(frase,"")
	for index,elem in enumerate(tags):
		tags_sentence += elem + " "
	relacoes = filter_amazon(tags_sentence,tokens)
	print(relacoes)
	imprime_relacao_2(primeira_entidade,segunda_entidade,relacoes)

def read_lines(input_file):
	with open (input_file,"r") as f:
		for line in f:
			currente =[]
			currente.append(line)
			#print(line)
			test_line(currente)
			#print("####################")

def test_line(line):
	tokens,tags,lemas,entidades,np = full_pipe(line,"")
	for index,elem in enumerate(tokens):
		if(tokens[index]=='\n'):
			break
		#print(tokens[index],tags[index],lemas[index],entidades[index])
	#print("##################")
	for index,elem in enumerate(tokens):
		if(elem[-1]=="-"):
			tags[index-1],tags[index] = tags[index],tags[index-1]
			tokens[index-1],tokens[index] = tokens[index],tokens[index-1]
		#print(elem,tokens[index])
	#print(tags)
	ent1=""
	end_token = []
	inicio = 0
	final_token = 0
	ents_joined = []
	start_token = []
	tipo_entidades = []
	for index, elem in enumerate(entidades):
		if(elem!="O"):
			if(elem[0]=="B"):
				inicio = 1
				tipo_entidades.append(elem.split("-")[1])
				ent1+=tokens[index]+" "
				final_token = index
				start_token.append(index)
			elif(elem[0]=="I" and inicio==1):
				ent1+=tokens[index]+" "
				final_token = index
		else:
			if(ent1!=""):
				ents_joined.append(ent1)
				ent1 = ""
				inicio=0
				end_token.append(final_token)
	#print(ents_joined)
	#print(tipo_entidades)
	perguntas_geradas = []
	if(len(ents_joined)>1):
		for i in range(len(ents_joined)-1):
			tags_sentence = ""
			verbos=[]
			for index,elem in enumerate(tags[(end_token[i]):start_token[i+1]]):
				if(elem[0]=="v"):
					lista_palavras = tokens[end_token[i]:start_token[i+1]]
					verbos.append(lista_palavras[index])
				tags_sentence += elem + " "
			#print("---" + str(tokens[(end_token[i]+1):start_token[i+1]])+"---")
			relacoes = filter_amazon(tags_sentence,tokens[end_token[i]:start_token[i+1]])
			#print(relacoes)
			#imprime_relacao_2(ents_joined[i],ents_joined[i+1],relacoes)
			entidades_for_triple = []
			entidades_for_triple.append(ents_joined[i])
			entidades_for_triple.append(ents_joined[i+1])

			tipo_entidades_for_triple = []
			tipo_entidades_for_triple.append(tipo_entidades[i])
			tipo_entidades_for_triple.append(tipo_entidades[i+1])

			for relacao in relacoes:
				#print(relacao)
				triplo = Triple_Frame(entidades_for_triple,relacao,tipo_entidades_for_triple,verbos,"templates.txt")
				perguntas_geradas.append(triplo.escolhe_de_template())
				#print(triplo.question_from_template("Onde <relacao> <entidade> ?",0)
	return perguntas_geradas

def test_file(input_file,out_file):
	tokens,tags,lemas,entidades,np = full_pipe(input_file,out_file)
	#print(tokens)
	#print(len(entidades))
	tags_sentence = ""
	for index,elem in enumerate(tokens):
		if(elem[-1]=="-"):
			tags[index-1],tags[index] = tags[index],tags[index-1]
			tokens[index-1],tokens[index] = tokens[index],tokens[index-1]
	for index,elem in enumerate(tags):
		tags_sentence += elem + " "
		#print(elem,tokens[index])
	#print(tags_sentence)
	inicio = 0
	primeira_entidade = []
	segunda_entidade = []
	#print(entidades)
	ent1 = ""
	ent2 = ""
	for index,elem in enumerate(entidades):
		if(elem!="O"):
			if(elem[0]=="B" and inicio == 0):
				inicio = 2
				ent1+=tokens[index]+" "
				#primeira_entidade.append(tokens[index])
			elif(elem[0]=="I" and inicio==2):
				ent1+=tokens[index]+" "
				#primeira_entidade.append(tokens[index])
			elif(elem[0]=="B" and inicio != 0):
				ent2+=tokens[index]+" "
				#segunda_entidade.append(tokens[index])
			elif(elem[0]=="I" and inicio != 0):
				ent2+=tokens[index]+" "
				#segunda_entidade.append(tokens[index])
		else:
			if(ent1!=""):
				primeira_entidade.append(ent1)
				ent1 = ""
			if(ent2!=""):
				segunda_entidade.append(ent2)
				ent2 = ""
	print(primeira_entidade)
	print(segunda_entidade)
	for i in range(len(primeira_entidade)):
		#print("Entidade 1:" + str(primeira_entidade[i]))
		#print("Entidade 2:" + str(segunda_entidade[i]))
		print("\n")
		relacoes = filter_amazon(tags_sentence,tokens)
		#print(relacoes)
		imprime_relacao_2(primeira_entidade[i],segunda_entidade[i+1],relacoes)
		print("#####")

def generate_from_input(input):
	return (test_line([input]))

if __name__ == '__main__':
	#ler_ficheiro_testes("ReRelemInSentences.txt")
	#test_file("testes.txt","testes.txt")
	#read_lines("testes5.txt")
	print(test_line(["O João Diogo estuda em Coimbra."])[0][0])
		
	'''
	with open("exemplos.txt","r") as f:
		for line in f:
			print(line)
			test_line([line.replace("\n","")])
	
	with open("exemplos.txt","r") as f:
		for line in f:
			print(line)
			prec,abran,f1 = test_line(line)
			global_prec += prec
			global_abran += abran
			global_f1 += f1

	print("\n############\n")
	print("Precisão:")
	print(str(global_prec))
	print("Abrangência:")
	print(str(global_abran))
	print("F-1:")
	print(str(global_f1))
	'''
