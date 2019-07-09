from block_switch_base import block_switch_base

class block_switch_block(block_switch_base):
	def __init__(self, line, coords, cases):
		self.line = line
		self.coords = coords
		self.cases = cases
		
		super(block_switch_block, self).__init__()
		
	def case_condition(self, func, block_state):
		return 'block {} {}'.format(self.coords.get_value(func), block_state)
		
	def compile_block_case(self, func, block):
		index = 0
		
		block_func = func.create_child_function()
	
		for block_state in self.block_list[block]:
			index += 1
		
			id = self.block_state_ids[block_state]
			case = self.block_state_list[block_state]
			falling_block_nbt = self.falling_block_nbt[block_state]
			
			case_func = block_func.create_child_function()
			try:
				case.compile(block_state, id, case_func, falling_block_nbt)
			except CompileError as e:
				print(e)
				raise CompileError('Unable to compile block switch at line {}'.format(self.line))
				
			single_command = case_func.single_command()
			if single_command:
				block_func.add_command('execute if {} run {}'.format(self.case_condition(block_func, block_state), single_command))
			else:
				unique = block_func.get_unique_id()
				case_name = 'line{:03}/case_{}{}_{:03}'.format(self.line, block.replace('minecraft:',''), index, unique)
				block_func.add_command('execute if {} run function {}:{}'.format(block_func.namespace, case_name))
				block_func.register_function(case_name, case_func)
				
		single_command = block_func.single_command()
		
		if single_command:
			func.add_command(single_command)
		else:
			unique = block_func.get_unique_id()
			block_case_name = 'line{:03}/case_{}_base_{:03}'.format(self.line, block.replace('minecraft:',''), unique)
			func.add_command('execute if block ~ ~ ~ {} run function {}:{}'.format(block, func.namespace, block_case_name))
			func.register_function(block_case_name, block_func)
				
	def get_range_condition(self, func, blocks):
		unique = func.get_unique_id()
		block_tag_name = 'switch_{}'.format(unique)
		func.register_block_tag(block_tag_name, [block.replace('minecraft:', '') for block in blocks])
		
		return 'block {} #{}:{}'.format(self.coords.get_value(func), func.namespace, block_tag_name)
		
	def get_case_ids(self):
		return sorted(self.block_list.keys())