from data_preparation.preparation import CodingTaskTemplate
from prompt_augmentation import back_translation, cloze, paraphrase
from code_generation.chatGPT_generated import CodeGenerator
from SAST_integration.bandit_scan import BanditScan
from prompt_scoring.scoring import PromptScoring



back_translate = back_translation.BackTranslation()
cloze_augment = cloze.Cloze()
paraphrase_augment = paraphrase.Paraphraser()



def f_gps(prompt_id, prompt, D_dev, bandit_scan, code_generator):
    """ calculate the fitness of a prompt based on Ddev dataset """ 
    if not isinstance(bandit_scan, BanditScan):
        raise TypeError("Expected an object of type BanditScan")
    if not isinstance(code_generator, CodeGenerator):
        raise TypeError("Expected an object of type CodeGenerator")
    
    # the final prompt score calculated over D_dev set
    prompt_score = 0

    # joining the preprompt with the code tasks in the D_dev
    template = CodingTaskTemplate()
    D_dev_task_templates = template.pre_template(D_dev)

    # calculate score for each code task in D_dev and sum it up
    for template in D_dev_task_templates:
        # generate code for the task template
        code = code_generator.generate_code(template)
        if code:
            # write the generated code to a python file
            code_file_path = code_generator.write_code_to_file(prompt_id, prompt, code)
        else:
            print(f"Code generation failed for {prompt_id}")
    if code_file_path:
        # perform bandit scan on the generated python file
        scan_output = bandit_scan.run_bandit(filepath=code_file_path)
        # add the scan output to the dictionary containing several prompt score infromation
        if scan_output:
            bandit_scan.process_scan_output(prompt_id=prompt_id, prompt=prompt, bandit_output=scan_output)
    
    scoring = PromptScoring()
    # calculate the score of the prompt on the current task
    score = scoring.bandit_score(prompt_id=prompt_id, bandit_scan=bandit_scan)
    if isinstance(score, int):
        prompt_score += score
    else:
        print(f"Prompt score is invalid for prompt: {prompt_id}")

    return prompt_score
        

def g_gps(prompts_to_augment):
    """ function to perform prompt augmentation"""
    augmented_prompts = []
    for prompt in prompts_to_augment:
        for lang in back_translate.languages:
            try:
                translated_prompt = back_translate.augment_prompt(prompt=prompt, source_lang='en', target_lang=lang)
            except Exception as error:
                print(f"An error occurred during back translation of prompt '{prompt}'. Error: {error}")
                return None
            if isinstance(translated_prompt, str):
                augmented_prompts.append(translated_prompt)
        for i in range(4):
            try: 
                clozed_prompt = cloze_augment.augment_prompt(prompt)
            except Exception as error:
                print(f"An error occured while performing cloze style augmentation of prompt '{prompt}, Error: {error}")
            if isinstance(clozed_prompt, str):
                augmented_prompts.append(clozed_prompt)
        try:
            paraphrased_prompts = paraphrase_augment.augment_prompt(prompt=prompt, num_beams=5, num_return_sequences=5)   
        except Exception as error:
            print(f"An error occured while paraphrasing the prompt '{prompt}, Error: {error}")
        for p in paraphrased_prompts:
            if isinstance(p, str):
                augmented_prompts.append(p)

    unique_prompts = paraphrase_augment.remove_duplicate_prompts(prompts=augmented_prompts)
    return unique_prompts


def create_initial_population(G0, population_size):
    # Create an initial population based on the single starting prompt
    # slight variations of G0 to form a population; replace this with a more sophisticated approach
    population = [G0 + str(i) for i in range(population_size)]
    return population

def GPS_algorithm(G0, Ddev, f_gps, g_gps, T, K, population_size):
    # Step 1: Create an initial population based on the single starting prompt
    G_t = create_initial_population(G0, population_size)
    stored_G = []
    
    for t in range(T+1):
        stored_G.append(G_t)
        
        # Step 4: Calculate score for each prompt using fGPS
        scores = [f_gps(prompt, Ddev) for prompt in G_t]
        
        # Step 5: Select top K prompts as reproductive group
        reproductive_group = [x for _, x in sorted(zip(scores, G_t), reverse=True)][:K]
        
        # Step 6: Generate G_t+1 based on reproductive group using gGPS
        G_t = g_gps(reproductive_group)
    
    # Step 8: Select top K prompts from all stored generations using gGPS
    all_prompts = [prompt for G in stored_G for prompt in G]
    all_scores = [f_gps(prompt, Ddev) for prompt in all_prompts]
    GT_plus_1 = [x for _, x in sorted(zip(all_scores, all_prompts), reverse=True)][:K]

    # Step 9: Return the final optimized prompts
    return GT_plus_1

# Step 1: Obtain handcrafted single prompt G0 as initialization
G0 = "starting prompt"

# Development dataset
Ddev = []  # Replace with your development dataset

# Number of generations
T = 5

# Number of top prompts to select
K = 2

# Population size for initialization
population_size = 5

# Run the GPS algorithm
optimized_prompts = GPS_algorithm(G0, Ddev, f_gps, g_gps, T, K, population_size)
print("Final optimized prompts:", optimized_prompts)
