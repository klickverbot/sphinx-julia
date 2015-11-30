import os
import subprocess
import model

# scriptname_parsefile = "scripts/sourcefile2pythonmodel.jl"
# scriptname_parseabstracttype = "scripts/parse_abstracttype.jl"

scriptdir = "scripts"
scripts = {
    "file": "sourcefile2pythonmodel.jl",
    "abstracttype": "parse_abstracttype.jl",
    "compositetype": "parse_compositetype.jl",
    "module": "parse_module.jl",
    "function": "parse_function.jl"
}

eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}

class JuliaParser:
    cached_files = {}

    def parsefile(self, sourcepath):
        if not os.path.exists(sourcepath):
            raise ValueError("Can't find file: " + sourcepath)
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptname_parsefile)
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        model = eval(buf, eval_environment)
        self.cached_files[sourcepath] = model
        return model

    def functions_from_file(self, sourcepath):
        if sourcepath in self.cached_files:
            d = self.cached_files[sourcepath]
        else:
            d = self.parsefile(sourcepath)
        return d

    def function_from_file(self, sourcepath, functionname):
        if sourcepath in self.cached_files:
            d = self.cached_files[sourcepath]
        else:
            d = self.parsefile(sourcepath)
        for func in d:
            if func["qualifier"]+"."+func["name"] == functionname:
                return func
        for func in d:
            if func["name"] == functionname:
                return func
        errortext = "Function {} not found in: {}"
        raise ValueError(errortext.format(functionname, sourcepath))

    def parsefunction(self, functionstring):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptname_parsefunc)
        p = subprocess.Popen(["julia", scriptpath, functionstring],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        function = eval(buf)
        return function

    def parsestring(self, objtype, text):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts[objtype])
        p = subprocess.Popen(["julia", scriptpath, text],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        model = eval(buf, eval_environment)
        return model

# eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}
# print(eval_environment)
# j = JuliaParser()
# model = j.parsefile("src/model.jl")
# model = j.parsefile("src/reader_file.jl")
# print(model)