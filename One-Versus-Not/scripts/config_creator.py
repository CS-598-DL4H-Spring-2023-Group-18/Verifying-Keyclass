import yaml

with open('base_config_mimic.yaml','r') as f:
    contents = yaml.load(f, Loader=yaml.Loader)
    for i in range(0,19):
        contents['n_class_being_tested'] = i
        newFileName = "config_mimic_"+str(i)+".yaml"
        with open(newFileName,'w') as outputFile:
            yaml.dump(contents, outputFile)

