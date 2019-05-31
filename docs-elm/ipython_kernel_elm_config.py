import os.path
import tempfile
import logging

c = get_config()    # noqa - defined by traitlets


class BaseFilter:
    """
    This is the reference implementation for all filters/hooks.
    Just passes the data as-is without changing it.
    """
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

    # This is called from the kernel before returning completion data
    def process_completion(self, code, cursor_pos, completion_data):
        """
        This is called from the kernel before returning completion data
        completion_data is a dict like
        {
            'matches' : matches,
            'cursor_end' : cursor_pos,
            'cursor_start' : cursor_pos - len(txt),
            'metadata' : {},
            'status' : 'ok'
        }
        """
        return completion_data


class SampleFilter(BaseFilter):
    def register(self, kernel, shell):
        super().register(kernel, shell)

        ident = kernel.ident

        logfile = os.path.join(tempfile.gettempdir(), 'elm-kernel-{}.log'.format(ident))

        logger = self.logger = logging.getLogger('elm-kernel-{}'.format(ident))
        fh = self.fh = logging.FileHandler(logfile)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
        logger.info('STARTED ELM SESSION {}'.format(ident))

        kernel.log.info("FILTER REGISTERED for elm-kernel {}".format(ident))
        kernel.log.info("LOGGING USER INTERACTIONS TO {}".format(logfile))

    def process_text_input(self, lines):
        output = []
        for line in lines:
            self.logger.info('LINE INPUT FROM USER: {}'.format(repr(line)))
            if 'FORBIDDEN_WORD' in line:
                line = line.replace('FORBIDDEN_WORD', 'SAFE_WORD')
                self.logger.info('LINE INPUT FROM USER: "FORBIDDEN_WORD" found, replacing with "SAFE_WORD"')
            output.append(line)

        self.fh.flush()
        return output

    # Simple exclusion from command history, try for example:
    # In [1]: print('something to exclude... no-history')
    def process_run_cell(self, code, options):
        if 'no-history' in code:
            options['store_history'] = False
            self.logger.info('RUN CODE, excluded from command history: {}'.format(repr(code)))
            self.fh.flush()
        return code

    def process_completion(self, code, cursor_pos, completion_data):
        self.logger.info('COMPLETION REQUESTED FOR: {}'.format(repr(code)))
        self.fh.flush()
        return completion_data


sample_filter = SampleFilter()

c.IPKernelApp.log_level = 'INFO'
c.IPythonKernel.code_filters = [sample_filter]
