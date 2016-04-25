import numpy
import pyopencl as cl


class NaiveSearchPOCL:
    """ Implementation of Naive search algorithm using OpenCL """

    def __init__(self, text, pieces_number=1):
        self.text = text
        self.text_len = len(text)
        self.pieces_num = pieces_number

    def all_matches(self, pattern, device_type=1):
        # Set up OpenCL
        # 0 - means for GPU
        # 1 - means for GPU
        # otherwise - some of the devices
        if device_type == 0:
            platform = cl.get_platforms()
            devices = platform[0].get_devices(cl.device_type.GPU)
            context = cl.Context(devices)
        elif device_type == 1:
            platform = cl.get_platforms()
            devices = platform[0].get_devices(cl.device_type.CPU)
            context = cl.Context(devices)
        else:
            context = cl.create_some_context(False)  # don't ask user about platform

        queue = cl.CommandQueue(context)

        with open("Pyopencl/naive/resources/naive_pocl.cl", "r") as kernel_file:
            kernel_src = kernel_file.read()

        program = cl.Program(context, kernel_src).build()

        if (self.text_len/self.pieces_num <= len(pattern)) or (self.pieces_num > self.text_len):
            raise ValueError("Choose less number of pieces as one piece length less than pattern length "
                             "or pieces number is more than string length")

        # initialize the result array
        matches = numpy.zeros(self.text_len).astype(numpy.int)

        # Create the input (string, pattern) strings in device memory and copy data from host
        d_str = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.text.encode())
        d_pat = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=pattern.encode())
        # Create the output (matches) string in device memory
        d_matches = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, matches.nbytes)
       
        search = program.naive_search
        search.set_scalar_arg_dtypes([None, None, int, int, None])
        search(queue, (self.text_len, ), 256, d_str, d_pat, self.text_len, len(pattern), d_matches)

        # Wait for the commands to finish before reading back
        queue.finish()

        # Read back the results from the compute device
        cl.enqueue_copy(queue, matches, d_matches)
        return matches


if __name__ == "__main__":
    obj = NaiveSearchPOCL("AAAABBB")
    obj.all_matches("A")