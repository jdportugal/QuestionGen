import nlpnet
import numpy as np
from FullPipeline import * 
from nltk.translate.bleu_score import sentence_bleu
from QuestionGenerationReverb import *

srl_encontradas = 0

nlpnet.set_data_dir('Perguntas/srl-pt/')

def metricas_Bleu(original,obtida):
	obtida = obtida.lower()
	obtida = obtida.split(":")[1]
	original = original.lower().replace("\n","")
	obtida = obtida[1:].lower().replace("\n","")
	#print(original)
	#print(obtida)
	original = original.replace("?","").split(" ")
	obtida = obtida.replace(" ?","").split(" ")
	#Neste caso a considera unigramas so (weights == 1)
	#print(original,obtida)

	print('Individual 1-gram: %f' % sentence_bleu([original], obtida, weights=(1, 0, 0, 0)))
	print('Individual 2-gram: %f' % sentence_bleu([original], obtida, weights=(0, 1, 0, 0)))
	print('Individual 3-gram: %f' % sentence_bleu([original], obtida, weights=(0, 0, 1, 0)))
	print('Individual 4-gram: %f' % sentence_bleu([original], obtida, weights=(0, 0, 0, 1)))
	score = sentence_bleu([original],obtida, weights=(1, 0, 0, 0))
	return score

##################################
#Estas metricas não estão a ser usadas
##################################

def metricas_Bleu_media(original,todas_obtidas):
	score = 0
	contagem = 0
	original = original.lower().replace("\n","")
	original = original.replace("?","").split(" ")
	for obtida in todas_obtidas:
		obtida = obtida.lower()
		obtida = obtida.split(":")[1]
		obtida = obtida[1:].lower().replace("\n","")
		#print(original)
		#print(obtida)
		obtida = obtida.replace(" ?","").split(" ")
		#Neste caso a considera unigramas so (weights == 1)
		#print(original,obtida)
		score += sentence_bleu([original],obtida, weights=(1, 0, 0, 0))
		contagem += 1
	#print("\n\n Bleu médio \n\n")
	#print(str(score/contagem))
	return score

def metricas_Bleu_max(original,todas_obtidas):
	bleu_max = 0
	score = 0
	contagem = 0
	original = original.lower().replace("\n","")
	original = original.replace("?","").split(" ")
	for obtida in todas_obtidas:
		obtida = obtida.lower()
		obtida = obtida.split(":")[1]
		obtida = obtida[1:].lower().replace("\n","")
		#print(original)
		#print(obtida)
		obtida = obtida.replace(" ?","").split(" ")
		#Neste caso a considera unigramas so (weights == 1)
		#print(original,obtida)
		score = sentence_bleu([original],obtida, weights=(1, 0, 0, 0))
		if(score>bleu_max):
			bleu_max = score
		contagem += 1
	#print("Bleu Max: \n")
	#print(str(bleu_max))
	return bleu_max


def precision_sentence(obtained,expected):
	conjunto_comum = []
	for palavra in obtained:
		if(palavra in expected):
			conjunto_comum.append(palavra)
	precision = len(conjunto_comum)/len(obtained)
	#print (precision)
	return precision

def accuracy_sentence(obtained,expected):
	conjunto_comum = []
	for palavra in obtained:
		if(palavra in expected):
			conjunto_comum.append(palavra)
	#print(conjunto_comum)
	accuracy = len(conjunto_comum)/len(expected)
	#print (accuracy)
	return accuracy

def f1_sentence(precision,accuracy):
	f1 = 2*(precision*accuracy)/(precision+accuracy)
	#print(f1)
	return f1

##################################
#Geração de perguntas a usar SRL
##################################

def gera_pergunta_tempo(arg1,argtime,v,frase,arg0,tm,aditional_args):
	verb_string = ""
	arg1_string = ""
	arg0_string = ""
	tm_string = ""
	aditional_args_string = ""
	for word in v:
		verb_string+=word+" "
	for word in arg1:
		arg1_string+=word+" "
	for word in arg0:
		arg0_string+=word+" "
	for word in tm:
		tm_string+=word+" "
	for part in aditional_args:
		for word in part:
			aditional_args_string+=word+" "
	pergunta = "P: Quando " + verb_string + arg1_string + arg0_string+aditional_args_string + "?"
	resposta = "R: " + tm_string +".\n"
	return pergunta,resposta

def gera_pergunta_local(arg1,argtime,v,frase,arg0,arglocal,aditional_args):
	verb_string = ""
	arg1_string = ""
	arg0_string = ""
	local_string = ""
	aditional_args_string = ""
	for word in v:
		verb_string+=word+" "
	for word in arg1:
		arg1_string+=word+" "
	for word in arg0:
		arg0_string+=word+" "
	for word in arglocal:
		local_string+=word+" "
	for part in aditional_args:
		for word in part:
			aditional_args_string+=word+" "
	pergunta = "P: Onde " + verb_string + arg1_string + arg0_string+ aditional_args_string +"?"
	resposta = "R: " + local_string +".\n"
	return pergunta,resposta

def gera_pergunta(arg0,arg1,v,frase,tipo,aditional_args):
	verb_string=""
	arg1_string=""
	arg3_string=""
	aditional_args_string = ""
	for word in v:
		verb_string+=word+" "
	for word in arg1:
		arg1_string+=word+" "
	for word in arg0:
		arg3_string+=word+" "
	for part in aditional_args:
		for word in part:
			aditional_args_string+=word+" "
	pergunta="P: "
	if(tipo=="PESSOA"):
		pergunta = "P: Quem "
	pergunta += verb_string + arg1_string + aditional_args_string+"?\n"
	resposta = "Q: "+arg3_string+"."
	return pergunta,resposta

##################################
#Geração de perguntas a usar NER e templates
##################################
def gera_perguntas_com_entidade(arg1,v,entidades,tipo,tokens):
	verb_string=""
	arg1_string=""
	entidade_conjunta = []
	entidade_temp = ""
	inicio = 0
	for word in v:
		verb_string+=word+" "
	for word in arg1:
		arg1_string+=word+" "
	for index,word in enumerate(entidades):
		if(tokens[index] not in arg1):
			if(inicio==0):
				if(word[0]=="B"):
					entidade_temp+=tokens[index]+" "
					inicio=1
			elif(inicio==1):
				if(word[0]=="I"):
					entidade_temp+=tokens[index]+" "
				else:
					entidade_conjunta.append(entidade_temp)
					entidade_temp=tokens[index]+" "
	entidade_conjunta.append(entidade_temp)
	pergunta="P: "
	if(tipo=="PESSOA"):
		pergunta = "P: Quem "
	pergunta += verb_string + arg1_string +"?\n"
	resposta = "Q: "+str(entidade_conjunta)+"."
	return pergunta,resposta


##################################
#Processamento frase  - funcao principal
##################################
def testa_frase(frase,config_list,outfile="OutputsPerguntas/out.txt"):
	todas_perguntas = []
	todas_respostas = []
	tokens_sem_os = []
	entidades_sem_os = []

	########################################
	#Pre processamento com o NLPyPort e recolha de entidades
	########################################
	tokens,tags,lemas,entidades,np_tags = full_pipe_preload(frase,config_list)
	global srl_encontradas
	for index,i in enumerate(tokens):
		if(entidades[index]!="O"):
			tokens_sem_os.append(tokens[index])
			entidades_sem_os.append(entidades[index])
	print("Entidades encontradas: "+"\n")
	for index,elem in enumerate(entidades_sem_os):
		print(tokens_sem_os[index] + " " + entidades_sem_os[index]+"\n")


	########################################
	#Recolha das SRL
	########################################
	tagger = nlpnet.SRLTagger()
	sent = tagger.tag(frase)[0]
	if(len(sent.arg_structures)>0):
		srl_encontradas+=1
	print("Argumentos encontrados: "+"\n")
	print(str(sent.arg_structures)+"\n")
	verb = ""
	arg0 = ""
	arg1 = ""
	arg2 = ""
	argtm = ""
	arglc = ""
	other_modifiers = []

	for elem in sent.arg_structures:
		for part in elem:
			#print(part)
			if(isinstance(part,dict)):
				####################
				#Recolher os elementos de tipos predefinidos para usar
				####################
				for key in part:
					if(key=="A1"):
						arg1 = part[key]
					elif(key=="A0"):
						arg0 = part[key]
					elif(key=="A2"):	
						arg2 = part[key]
					elif(key=="V"):
						verb = part[key]
					elif(key=="AM-TMP"):
						other_modifiers.append(part[key])
						argtm = part[key]
					elif(key=="AM-LOC"):
						other_modifiers.append(part[key])
						arglc = part[key]



	pergunta=""
	resposta=""
	frases_totais = 0
	tipo_entidade=""

	####################################
	#So um argumento encontrado
	####################################
	if(arg1!=""  and verb!="" and arg0!=""):
		#adiciona outros modificadores a frase
		other_modifiers.append(arg2)
		for word in arg0:
			for index,elem in enumerate(tokens_sem_os):
				if(word ==elem):
					tipo_entidade = entidades_sem_os[index][2:]

		pergunta,resposta = gera_pergunta(arg0,arg1,verb,frase,tipo_entidade,other_modifiers)
		todas_perguntas.append(pergunta)
		todas_respostas.append(resposta)
		#print("Encontrados os argumentos arg1 e arg0")

	if(arg2!=""  and verb!="" and arg0!=""):
		#adiciona outros modificadores a frase
		other_modifiers.append(arg1)
		for word in arg2:
			for index,elem in enumerate(tokens_sem_os):
				if(word ==elem):
					tipo_entidade = entidades_sem_os[index][2:]

		pergunta,resposta = gera_pergunta(arg0,arg2,verb,frase,tipo_entidade,other_modifiers)
		todas_perguntas.append(pergunta)
		todas_respostas.append(resposta)

	if(arg1!=""  and verb!="" and arg2!=""):
		#adiciona outros modificadores a frase
		other_modifiers.append(arg0)
		for word in arg1:
			for index,elem in enumerate(tokens_sem_os):
				if(word ==elem):
					tipo_entidade = entidades_sem_os[index][2:]

		pergunta,resposta = gera_pergunta(arg2,arg1,verb,frase,tipo_entidade,other_modifiers)
		todas_perguntas.append(pergunta)
		todas_respostas.append(resposta)


	####################################
	#So um argumento (SRL) encontrado
	####################################
	if(arg1!="" and arg2==arg0==""):
		for word in arg1:
			for index,elem in enumerate(tokens_sem_os):
				if(word ==elem):
					tipo_entidade = entidades_sem_os[index][2:]
		pergunta,resposta=gera_perguntas_com_entidade(arg1,verb,entidades_sem_os,tipo_entidade,tokens_sem_os)
		todas_perguntas.append(pergunta)
		todas_respostas.append(resposta)

	if(arg2!="" and arg1==arg0==""):
		for word in arg2:
			for index,elem in enumerate(tokens_sem_os):
				if(word ==elem):
					tipo_entidade = entidades_sem_os[index][2:]
		pergunta,resposta=gera_perguntas_com_entidade(arg2,verb,entidades_sem_os,tipo_entidade,tokens_sem_os)
		todas_perguntas.append(pergunta)
		todas_respostas.append(resposta)

	if(arg0!="" and arg1==arg2==""):
		for word in arg0:
			for index,elem in enumerate(tokens_sem_os):
				if(word ==elem):
					print("Entidade encontrada do tipo " + entidades_sem_os[index]+"\n")
					tipo_entidade = entidades_sem_os[index][2:]
		pergunta,resposta=gera_perguntas_com_entidade(arg0,verb,entidades_sem_os,tipo_entidade,tokens_sem_os)
		todas_perguntas.append(pergunta)
		todas_respostas.append(resposta)

	####################################
	#Perguntas para argumentos do tipo tempo e local usando SRL
	####################################

	if(argtm!=""):
		other_modifiers = [arglc,arg2]
		if(arg1=="" and arg0!=""):
			pergunta,resposta = gera_pergunta_tempo(arg0,argtm,verb,frase,arg1,argtm,other_modifiers)
			todas_perguntas.append(pergunta)
			todas_respostas.append(resposta)
		if(arg1!="" and arg0==""):
			pergunta,resposta = gera_pergunta_tempo(arg1,argtm,verb,frase,arg0,argtm,other_modifiers)
			todas_perguntas.append(pergunta)
			todas_respostas.append(resposta)
		if(arg1!="" and arg0!=""):
			pergunta,resposta = gera_pergunta_tempo(arg0,argtm,verb,frase,arg1,argtm,other_modifiers)
			todas_perguntas.append(pergunta)
			todas_respostas.append(resposta)
	
	if(arglc!=""):
		other_modifiers = [argtm,arg2]
		if(arg1=="" and arg0!=""):
			pergunta,resposta = gera_pergunta_local(arg0,arglc,verb,frase,arg1,arglc,other_modifiers)
			todas_perguntas.append(pergunta)
			todas_respostas.append(resposta)
		if(arg1!="" and arg0==""):	
			pergunta,resposta = gera_pergunta_local(arg1,arglc,verb,frase,arg0,arglc,other_modifiers)
			todas_perguntas.append(pergunta)
			todas_respostas.append(resposta)
		if(arg1!="" and arg0!=""):
			pergunta,resposta = gera_pergunta_local(arg0,arglc,verb,frase,arg1,arglc,other_modifiers)
			todas_perguntas.append(pergunta)
			todas_respostas.append(resposta)

	####################################
	#Perguntas Utilizando entidades e templates
	####################################
	geracao_so_com_entidades = generate_from_input(frase)
	if(geracao_so_com_entidades!=[]):
		if(len(geracao_so_com_entidades[0][0])>0):
			geracao_so_com_entidades = geracao_so_com_entidades[0][0]
			pergunta = "P: " + str(geracao_so_com_entidades[0])
			resposta = "R: "+str(geracao_so_com_entidades[1])
			frases_totais+=1


	return todas_perguntas,todas_respostas,frases_totais


##################################
#Processamento do ficheiro - passa frase
##################################
def processa_ficheiro(input,outfile="OutputsPerguntas/out.txt"):
	config_list = load_congif_to_list()
	testa = True
	total_prec = []
	total_ac = []
	total_f1 = []
	frase_currente = ""
	pergunta_currente = ""
	resposta_currente = ""
	frases_totais = 0
	total_inicial = 0
	bleu_final_score = 0
	bleu_final_medio_score = 0
	tested_questions = 0
	bleu_final_max_score = 0

	with open(input,"r") as f:
		for index,line in enumerate(f):
			if(len(line)>1):
				if(line[0]=="F"):
					############################
					#Recolher a frase de entrada
					############################
					frase_currente=line.split(":")[1]
					frase_currente=frase_currente.replace("\n","")
					print("------------------------------\n")
					print("F: "+ frase_currente+"\n")
					#print("F: "+ frase_currente)
					total_inicial+=1
					#print(entidades)
				elif(line[0]=="Q"):
					############################
					#Recolher a pergunta esperada
					############################
					pergunta_currente = line.lower()
					pergunta_currente = pergunta_currente.split(":")[1]
					pergunta_currente = pergunta_currente.replace("\n","")
				else:
					############################
					#Se a frase é a resposta, ja recolhemos antes a frase e a pergunta esperada e podemos agora fazer o processamento destas
					############################
					resposta_currente = line.split(":")[1]
					resposta_currente = resposta_currente.replace("\n","")
					

					############################
					#Processar a frase e obter as perguntas e repostas esperadas
					############################
					pergunta_gerada_original,resposta,frases_totais_temp = testa_frase(frase_currente,config_list,outfile)
					if(pergunta_gerada_original!=[]):
						frases_totais+=1
					pergunta_gerada = pergunta_gerada_original
					print("Pergunta esperada: " + str(pergunta_currente)+"\n")
					#print(pergunta_currente)
					print("Pergunta(s) gerada(s):" + str(pergunta_gerada)+"\n")
					#print(pergunta_gerada)
					print("Resposta(s) gerada(s):"+str(resposta)+"\n")
					#print(resposta)



					############################
					#Obter metricas
					############################
					if(testa==True):
						if(pergunta_gerada!=[]):
							tested_questions+=1
							current_bleu = metricas_Bleu(pergunta_currente,pergunta_gerada[0])
							bleu_medio = metricas_Bleu_media(pergunta_currente,pergunta_gerada)
							bleu_final_score+= current_bleu
							bleu_final_medio_score += bleu_medio
							bleu_max = metricas_Bleu_max(pergunta_currente,pergunta_gerada)
							bleu_final_max_score += bleu_max
					else:

						############################
						#Casos em que nenhuma pergunta foi gerada
						############################
						print("---------------")
						print("---------------")
					#print("\n############################\n")

	############################
	#Escrever metricas para ficheiro
	############################
	with open(outfile,"a") as g:
		g.write("Frases introduzidas: " + str(total_inicial)+"\n")
		g.write("Perguntas geradas: " + str(frases_totais)+"\n")
		g.write("Bleu final para as perguntas geradas: "+str(bleu_final_score/tested_questions)+"\n")


if __name__ == '__main__':
	processa_ficheiro("Perguntas/simple.txt","OutputsPerguntas/resultados_limpos.txt")
	print(srl_encontradas)
	'''
	while(1):
		g = input("Frase : ") 
		testa_frase(g)
	'''