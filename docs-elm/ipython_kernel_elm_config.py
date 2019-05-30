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
    def process_run_cell_parameters(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        pass


class SampleFilter(BaseFilter):
    def register(self, kernel, shell):
        super().register(kernel, shell)

        def logger_cmd(info):
            kernel.log.info('PRE RUN CELL: {}'.format(info))
            info.raw_cell = 'print(locals())'

        shell.events.register('pre_run_cell', logger_cmd)
        kernel.log.info("FILTER REGISTERED")

    def process_text_input(self, lines):
        output = []
        for line in lines:
            output.append(line.replace('FORBIDDEN_WORD', 'SAFE_WORD'))

        return output


sample_filter = SampleFilter()

c.IPKernelApp.log_level = 'INFO'
c.IPythonKernel.code_filters = [sample_filter]
