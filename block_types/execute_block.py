from execute_base import execute_base
from CompileError import CompileError
import traceback

class execute_block(execute_base):
	def __init__(self, line, exec_items, sub, else_list = []):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		self.else_list = else_list
		
	def compile(self, func):
		self.perform_execute(func)
		
	def display_name(self):
		return 'execute'
		
	def add_continuation_command(self, func, func_name, exec_func):
		if len(self.else_list) > 0:
			func.add_command('scoreboard players set Global {} 1'.format(self.scratch))
			exec_func.add_command('scoreboard players set Global {} 0'.format(self.scratch))
			
	def force_sub_function(self):
		return len(self.else_list) > 0
		
	def prepare_scratch(self, func):
		if len(self.else_list) > 0:
			self.scratch = func.get_scratch()
	
	def compile_else(self, func):
		if len(self.else_list) == 0:
			return
		
		for idx in range(len(self.else_list)):
			execute_items, else_sub = self.else_list[idx]
			exec_func = func.create_child_function()
			
			try:
				exec_func.compile_blocks(else_sub)
			except CompileError as e:
				print(e)
				raise CompileError('Unable to compile else block contents at line {}'.format(self.display_name(), self.line))
			except Exception as e:
				print(traceback.format_exc())
				raise CompileError('Unable to compile else block contents at line {}'.format(self.display_name(), self.line))
				
			if execute_items == None:
				exec_text = ''
			else:
				exec_text = func.get_execute_items(execute_items, exec_func)
			prefix = 'execute if score Global {} matches 1.. {}'.format(self.scratch, exec_text)
			if idx < len(self.else_list) - 1:
				# There are more else items, so make sure we don't run them
				exec_func.add_command('scoreboard players set Global {} 0'.format(self.scratch))

			single = exec_func.single_command()
			if single == None:
				unique = func.get_unique_id()
				func_name = 'else{0:03}_ln{1}'.format(unique, self.line)
				func.register_function(func_name, exec_func)
				
				func.add_command('{}run function {}:{}'.format(prefix, func.namespace, func_name))
			else:
				if single.startswith('/'):
					single = single[1:]
					
				if single.startswith('execute '):
					func.add_command(prefix + single[len('execute '):])
				else:
					func.add_command(prefix + 'run ' + single)
				
		func.free_scratch(self.scratch)