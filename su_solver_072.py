import numpy as np
import pandas as pd
from itertools import combinations

def get_cell_from_matrix(r,c,nums):
    #returns cell from matrix which is list of lists
    #r - row number from 0
    #c - column number from 0
    return nums[r][c]

def generate_rows_and_cols(nrows=9,ncols=9):
    #returns coordinates of all rows and cols
    rows = []
    cols = []
    for r in range(nrows):
        row = []
        col= []
        for c in range(ncols):
            row.append([r,c])
            col.append([c,r])
        rows.append(row)
        cols.append(col)       
    return(rows,cols)

def generate_squares(size=9,sq_s=3):
    #returns coordinates of points in 9 subsquares 3x3
    sq_size =[]
    while sq_s <= size:
        sq_size.append(sq_s)
        sq_s = sq_s  +3    
    sqs = []
    for x in sq_size:
        for y in sq_size:
            sq=[]
            for r in range(x-3,x):
                for c in range(y-3,y):
                    sq.append([r,c])
            sqs.append(sq)
    return sqs

def read_data(filepath,dim=9):
    #reads starting data from textfile
    #returns matrix with known and unknown sudoku vals
    with open(filepath) as f:
        su_data = f.readlines()
     
    su_data = [r.replace(' ','') for r in su_data]
    su_data = [r.replace('\n','') for r in su_data]
    su_data = [r.replace('X','0') for r in su_data]
    su_data = ''.join(su_data)
    
    su = np.eye(dim)
    
    for r in range(dim):
        for c in range(dim):
            su[r,c] = int(su_data[r*dim+c])
    return su

def create_start_data(su_matrix,dim = 9):
    #returns list of lists in row / column shape for sudoku
    #first list element is value of cell, 0 if unknown
    nums = [[[] for x in range(dim)] for x in range(dim)]
    for r in range(dim):
        for c in range(dim):
            nums[r][c].append(int(su_matrix[r][c]))
    return nums


def extract_group_vars(r,c,group,matrix):
    #r - row point coords, c - col points coords
    #group- list of all columns or rows or squares
    #matrix - matrix of known and unknowkn sudoku vals
    group_coords = [x for x in group if [r,c] in x] # coords of all points in group
    group_coords = group_coords[0]
    group_vals = [get_cell_from_matrix(x[0],x[1],nums)[0] for x in group_coords]
    return group_vals # all values for group


def extract_all_vars(r,c,groups,matrix):
    #returns all unique values that specified point CAN NOT have 
    #(because are take by known values of that point's row / col / square)
    vals = []
    for gr in groups:
        vals_tmp = extract_group_vars(r,c,gr,matrix)
        vals = vals + vals_tmp
        vals = list(set(vals))
        vals = [v for v in vals if v != 0]
    return vals

def update_data_remove_pairs(nums,groups,all_pairs):
    #finds pairs that occur exactly two times in group.
    #removes numbers found in such pair from other cells in group
    for group in groups: 
        for element in group:
            for pair in all_pairs:
                n=0
                for coords in element:
                    if nums[coords[0]][coords[1]][0] == 0:
                        if pair == nums[coords[0]][coords[1]][2]:
                            n = n+1
                if n==2:
                    print("usunieto pary {}".format(pair))
                    for coords in element:
                        #print(coords)
                        if nums[coords[0]][coords[1]][0] == 0:
                            if pair != nums[coords[0]][coords[1]][2]:
                                #print(nums[coords[0]][coords[1]][2])
                                nums[coords[0]][coords[1]][2] = [val for val in nums[coords[0]][coords[1]][2] if val not in pair] 
    return nums




def update_data_possible_nums(nums,dim=9):
    all_nums = [1,2,3,4,5,6,7,8,9]
    #adds list of possible and unpossible numbers on each position
    for r in range(dim):
        for c in range(dim):
            if get_cell_from_matrix(r,c,nums)[0] == 0:
                taken_vals = extract_all_vars(r,c,[rows,cols,sqs],su)
                free_vals = [x for x in all_nums if x not in taken_vals]
                if len(nums[r][c])==1:
                    nums[r][c].append(taken_vals)
                    nums[r][c].append(free_vals)
                else:    
                    nums[r][c][1] = taken_vals
                    nums[r][c][2] = free_vals
    return nums

def get_missing_n(nums):
    #returns number of missing values 
    missing = 0
    for r in nums:
        for c in r:
            if c[0]==0:
                missing = missing +1
    return missing
                
def print_sudoku(nums,su):
    su_pd =pd.DataFrame(su)
    all_columns = list(su_pd) # Creates list of all column headers
    su_pd[all_columns] = su_pd[all_columns].astype(float).astype(int).astype(str)
    for r in range(9):
        for c in range(9):
            val=str(nums[c][r][0])
            if val == '0':
                val = 'X'
            su_pd[r][c] =  val   
    print(su_pd)

def solve_unique_vals(nums,groups,print_steps = True):
    updated = 0
    for group in groups: 
        for element in group:
        ##for each cell in group (row,col or sq) extracts it's posible values
        ##list 'possible numbers' contains possible values for all cels in row,col or sq
            possible_numbers = []
            combinations = []
            for coords in element:
                #print(coords)
                num = get_cell_from_matrix(coords[0],coords[1],nums)
                if num[0] != 0:
                    pos_numbers = []
                else:
                    pos_numbers = num[2]
                #print('coords = {}, pos_numbers = {}'.format(coords,pos_numbers))
                possible_numbers = possible_numbers + pos_numbers
                combinations.append(pos_numbers)
                #print(combinations)
                combinations = [c for c in combinations if len(c)==2]
                #print(combinations)
            
            ##if specific value occurs only once in possible_values, then a cell can be updated
            ##(it means that no other cell in row/cols/sq can have this value)
            for i in range(1,10):
                #print(i)
                n = possible_numbers.count(i) #checks nof occurencies of value in possible_numbers
                if n ==1:
                    for coords in element: #looks for cell which can have value that occured only once in possible_numbers
                        cell = get_cell_from_matrix(coords[0],coords[1],nums)
                        if cell[0] == 0 and i in cell[2]:
                            nums[coords[0]][coords[1]] = [i] #update cell
                            nums = update_data_possible_nums(nums,dim=9) #update possible values for each cell when one cell was updated
                            updated = updated +1
                            if print_steps:
                                print("Update value coords: {}".format(coords))
                                print("updated value = {}".format(i))
                                print_sudoku(nums,su)
    return nums,updated

def solve_only_vals(nums,updated,groups,print_steps = True):
    for r in range(9):
        for c in range(9):
            if nums[r][c][0] == 0:
                if len(nums[r][c][2]) == 1:
                    nums[r][c] = nums[r][c][2]
                    nums = update_data_possible_nums(nums,dim=9)  
                    updated = updated +1
                    if print_steps:
                        print("Update value coords: [{},{}]".format(r,c))
                        print("updated value = {}".format(nums[r][c]))
                        print_sudoku(nums,su)
    return nums, updated

def remove_hidden_pairs(all_pairs,groups):
    for group in groups: 
        for element in group:
            for pair in all_pairs:
                n=0
                n2=0
                for coords in element:
                    if nums[coords[0]][coords[1]][0] == 0:
                        if pair[0] in nums[coords[0]][coords[1]][2] and pair[1] in nums[coords[0]][coords[1]][2]:
                            n = n+1
                    if nums[coords[0]][coords[1]][0] == 0:
                        if pair[0] in nums[coords[0]][coords[1]][2] or pair[1] in nums[coords[0]][coords[1]][2]:
                            n2 = n2+1
                if n==2 and n2==2:                       
                    print("usunieto UKRYTE pary {}".format(pair))
                    print(element)
                    for coords in element:
                        #print(coords)
                        if nums[coords[0]][coords[1]][0] == 0:
                            if pair[0] in nums[coords[0]][coords[1]][2] and pair[1] in nums[coords[0]][coords[1]][2]:
                                nums[coords[0]][coords[1]][2] = [val for val in nums[coords[0]][coords[1]][2] if val in pair]
                                print(nums[coords[0]][coords[1]][2])
    return nums

def solve_sudoku(nums,groups,all_pairs,all_triples,print_steps = True):
    #iterates to solve sudoku
    missing = get_missing_n(nums)
    updated_before = 0
    updated = 0
    total_updated = 0
    while missing > 0: 
        missing = get_missing_n(nums)
        updated_before = 0+updated
        updated = 0

        nums, updated = solve_unique_vals(nums,groups,print_steps = True)
        nums, updated = solve_only_vals(nums,updated,groups,print_steps = True)
        nums = remove_hidden_pairs(all_pairs,groups) 

        #nums = update_data_remove_pairs(nums,groups,all_pairs)
        for r in range(9):
            for c in range(9):
                if nums[r][c][0] == 0 and nums[r][c][2] == []:
                    updated = 0
                    updated_before == 0 
                    missing = 99
                    print("ERRROR, r={},c={}".format(r,c))

        if updated == 0 and updated_before == 0 and missing > 0:
            print("Unable to solve next number, must stop here :(")
            print(total_updated)
            break
                    
    if print_steps==False:
        print_sudoku(nums,su)

def get_file_path():
    filePath = input("Enter path to text file with sudoku to be solved, eg C:\\Users\\user\\Desktopsu_input.txt\\n")
    return(filePath)
############

if __name__ == "__main__":
    all_vals = [1,2,3,4,5,6,7,8,9]
    all_pairs = [list(comb) for comb in combinations(all_vals, 2)]
    all_triples = [list(comb) for comb in combinations(all_vals, 3)]
    
    rows,cols = generate_rows_and_cols()    
    sqs = generate_squares()
    var_exists = 'su' in locals() or 'su' in globals()
    while var_exists == False:
        filePath = get_file_path()
        try:
            su = read_data(filePath)
        except:
            print('Invalid path or file, try again.')
        var_exists = 'su' in locals() or 'su' in globals()

    su = read_data(filePath)        
    nums = create_start_data(su,dim = 9)
    nums = update_data_possible_nums(nums)
    print("This is starting point:")
    print_sudoku(nums,su)
    input('Press ENTER to start solver.')
    solve_sudoku(nums,[rows,cols,sqs],all_pairs,all_triples)
    input('Press ENTER to exit.')

