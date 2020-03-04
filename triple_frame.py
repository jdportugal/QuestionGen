class Triple_Frame:
	def __init__(self,entities,relation,entities_type,verbs,template):
		self.entities = entities
		self.relation = ""
		for rel in relation:
			self.relation+= rel + " "
		self.relation = self.relation[:-1]
		self.entities_type = entities_type
		self.verbs = ""
		for verbo in verbs:
			self.verbs += verbo + " "
		self.verbs = self.verbs[:-1]
		self.template = template

	def escolhe_de_template(self):
		template1 = ""
		template2 = ""
		save_next = 0
		with open(self.template,"r") as f:
			for line in f:
				line = line.replace("\n","")
				if(save_next==0):
					if(line.split(" ")[0] == self.entities_type[0] and line.split(" ")[1] == self.entities_type[1]):
						save_next=1
				elif(save_next==1):
					save_next=2
					template1 = line
				elif(save_next==2):
					save_next = 0
					template2 = line
					break
		geradas = []
		#geradas.append(self.question_from_template(str(template1),0))
		geradas.append(self.question_from_template(str(template2),0))
		'''
		for elem in geradas:
			for part in elem:
				print(part)
		'''
		return(geradas)

	def question_from_template(self,template,inverted):
		#O João estuda em Coimbra
		#template normal : Onde <relacao> <entidade>
		if(inverted==0):
			pergunta = template
			pergunta = pergunta.replace("<relacao>", self.verbs)
			pergunta = pergunta.replace("<entidade>", self.entities[0])
			
			resposta = self.entities[1]
		#template invertido : Quem <relacao> <entidade>  
		else:
			pergunta = template
			pergunta = pergunta.replace("<relacao>", self.relation)
			pergunta = pergunta.replace("<entidade>", self.entities[1])
			
			resposta = self.entities[0]

		return [pergunta,resposta]



if __name__ == '__main__':
	triplo = Triple_Frame(["João","Coimbra"],"estuda em",["PESSOA","LOCAL"],["estuda"])
	print(triplo.question_from_template("Onde <relacao> <entidade> ?",0))
	print(triplo.question_from_template("Quem <relacao> <entidade> ?",1))