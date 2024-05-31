import json
import sys
import os

class CreateREADME:
    def __init__(self, inputFile, outputFile, pluginFileName):
        self.inputFile = inputFile
        self.space_for_desc = 50
        self.extra_space_for_desc = 75
        self.outputFile = outputFile
        self.pluginFileName = pluginFileName

    def get_spaces(self, line):
        spaces = ""
        if line:
            spaces_req = self.space_for_desc - len(line)
        else:
            spaces_req = self.space_for_desc
        if spaces_req > 0:
            while spaces_req:
                spaces += " "
                spaces_req -= 1
        else:
            spaces_req = self.extra_space_for_desc - len(line)
            while spaces_req > 0 and spaces_req:
                spaces += " "
                spaces_req -= 1

        return spaces

    def create_output_line(self, param_json):
        line = "\t" + param_json.get('name') + "(" + param_json.get('type') + ")"
        spaces = self.get_spaces(line)
        final_line = line + spaces + "- " + param_json.get('properties').get('description') + "\n"
        return final_line

    def write_plugin_parameters(self, outputf, parameters):
        outputf.write("Plugin Parameters :\n\n")
        if parameters:
            for parameter in parameters:
                if isinstance(parameter, list):
                    param_json = parameter[1]
                    output_line = self.create_output_line(param_json)
                    outputf.write(output_line)
                else:
                    print("parameter format is unexpected, it should be list")

    def create_command_parameter_line(self, param_json):
        line = "\t\t\t" + param_json.get('name') + "(" + param_json.get('type').replace(self.pluginFileName + ".",
                                                                                        "") + ")"
        spaces = self.get_spaces(line)
        final_line = line + spaces + "- " + param_json.get('properties').get('description') + "\n"
        return final_line

    def write_parameters(self, outputf, parameters, parameter_type):
        outputf.write("\t\t" + parameter_type + " -\n")
        if parameters:
            for parameter in parameters:
                if isinstance(parameter, list):
                    param_json = parameter[1]
                    output_line = self.create_command_parameter_line(param_json)
                    outputf.write(output_line)
                elif isinstance(parameter, dict):
                    output_line = self.create_command_parameter_line(parameter)
                    outputf.write(output_line)
                else:
                    print("input parameter format is unexpected, it should be list or dict")

    def write_plugin_commands(self, outputf, base_commands):
        outputf.write("Commands :\n")
        if base_commands:
            command_no = 0
            for base_command in base_commands:
                command_no += 1
                if isinstance(base_command, dict):
                    outputf.write("\n\t" + str(command_no) + ". " + base_command.get('name') + "\n")
                    outputf.write("\t\t" + base_command.get('description') + "\n")
                    self.write_parameters(outputf, base_command.get('input_parameters'), "input")
                    self.write_parameters(outputf, base_command.get('output_parameters'), "output")
                else:
                    print("base_command format is unexpected, it should be dict")
                    
    def createReadMe(self):
        with open(self.inputFile, 'r') as inputf:
            file_data = json.load(inputf)
            base_commands = file_data.get('base_commands')
            parameters = file_data.get('parameters')
            outputf = open(self.outputFile, "a")
            create_readme.write_plugin_parameters(outputf, parameters)
            outputf.write("\n")
            create_readme.write_plugin_commands(outputf, base_commands)
            outputf.close()


if __name__ == "__main__":
    inputDir = sys.argv[1]
    outputFile = sys.argv[2]
    pluginFileName = sys.argv[3]
    tar_files = os.listdir(inputDir)[0]
    inputDir = os.path.join(inputDir, tar_files)

    complexDataTypeJSON = []
    for f in os.listdir(inputDir):
        if f.endswith('.json') and f != "index.json":
            if len(f.split('.')) <= 2:
                inputFile = os.path.join(inputDir, f)
                create_readme = CreateREADME(inputFile, outputFile, pluginFileName)
                create_readme.createReadMe()
            else:
                complexDataTypeJSON.append(os.path.join(inputDir, f))

    # print(complexDataTypeJSON)
    # for json_file in complexDataTypeJSON:
    #     create_readme = CreateREADME(json_file, outputFile, pluginFileName)
    #     create_readme.createReadMe()