c = get_config()    # noqa - defined by traitlets


class BaseFilter:
    def register(self, kernel, shell):
        self.kernel = kernel
        self.shell = shell

        shell.input_transformers_cleanup.append(self.process_text_input)

        # You can also perform more advanced modifications, see:
        # https://ipython.readthedocs.io/en/stable/config/inputtransforms.html#ast-transformations

    def process_text_input(self, lines):
        return lines

    # This is called from the kernel before feeding input into the IPython Shell
    def process_run_cell(self, code, options):
        """
        Modifies the arguments and code passed to shell.run_cell()
        options is a dict like
        {
            'silent': False,
            'store_history': True,
            'user_expressions': None

        }
        that can be modified in place to change behaviour.
        Returns: the new code to run
        """
        return code


class SampleFilter(BaseFilter):
    def register(self, kernel, shell):
        super().register(kernel, shell)

        kernel.log.info("FILTER REGISTERED")

    def process_text_input(self, lines):
        output = []
        for line in lines:
            output.append(line.replace('FORBIDDEN_WORD', 'SAFE_WORD'))

        return output

    # Simple exclusion from command history, try for example:
    # In [1]: print('something to exclude... no-history')
    def process_run_cell(self, code, options):
        if 'no-history' in code:
            options['store_history'] = False
        return code


sample_filter = SampleFilter()

c.IPKernelApp.log_level = 'INFO'
c.IPythonKernel.code_filters = [sample_filter]
