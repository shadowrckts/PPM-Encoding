#PPM Encoder
import numpy as np
import math
import csv

def Encode(key, data, reprate, M, s_width):
    #Determine guard time
    frame_width = M*s_width #s/slot * slot = seconds data could occur in
    Tg = (1/reprate)-frame_width #Guard Time where no pulses are allowed to occur within
    print('The Guard Time is '+str(Tg)+' s.')

    #Timing initializer, 2 or 4 pulses that hover around the center
    init_points = 2 #N as described
    init_dat = np.zeros((init_points))
    if init_points == 2:
        init_dat = [(M/2)-1,(M/2)]
    else:
        init_dat = [0,M-1,(M/2)-1,(M/2)]
    keyread = []
    #initialize slots and timings, insert init vals
    with open(key, newline='') as csvfile:
        csvread = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in csvread:
            keyread.append(row)
    keyread = flatten(keyread)
    slot_nums = np.zeros(len(data))
    #Determine slots for each data point, if not included, "Null" is chosen
    for i in range(len(data)):
        if str(data[i]) not in keyread:
            if str(data[i]) == " ":
                slot_nums[i] = keyread.index('Space')
            else:
                print(str(data[i])+' is not located in the key file, encoding as "Null".')
                slot_nums[i] = keyread.index('Null')
        else:
            slot_nums[i] = keyread.index(str(data[i]))

    #Determine times for each data point, applies Tg to start data to give time prior to data
    slot_nums = np.concatenate((init_dat, slot_nums))
    data_times = np.zeros(len(slot_nums))
    for i in range(len(data_times)):
        if i == 0:
            data_times[i] = Tg + slot_nums[i]*s_width
        else:
            data_times[i] = Tg + data_times[i-1] + ((M-1)-slot_nums[i-1])*s_width + (slot_nums[i]*s_width) #Guard Time + Last Time + (Remaining slots in last frame) + (slots in this frame before this slot)

    return slot_nums, data_times, keyread, Tg

def flatten(xss):
    return [x for xs in xss for x in xs]

def ArbWave(filename, header, times, p_width, datalen, amp, timestep):
    #Create a dataset of length = datalen and pulses occuring at enc_dat times
    enc_dat = np.zeros([datalen,2])
    t_pos = np.zeros(len(times))
    p_width = math.ceil(p_width/timestep)
    for i in range(len(times)):
        t_pos[i] = math.ceil((times[i]/timestep)-1)
    in_pulse = 0
    k = 0
    #Raise to amp value at the start of the pulse, maintain it through p_width, then reset and wait
    for i in range(datalen):
            enc_dat[i][0] = i+1
            if i == t_pos[k] or in_pulse > 0:
                enc_dat[i][1] = amp
                in_pulse = in_pulse + 1
                if in_pulse >= p_width:
                    k = k + 1
                    in_pulse = 0
                    if k > len(t_pos)-1:
                        k = 0
    dat_write = header+(enc_dat.tolist())
    #writes the data to the end of the line
    with open(filename, 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerows(dat_write)
    return 

def Decoder(key,data, Tg, s_width, M):

    return

if __name__ == '__main__':

    #Initialize Important Variables
    reprate = 1000000 #Value in Hz
    M = 64 #Number of Slots, must be >= number of items in your key, integer value
    s_width = 10E-9 #Slot width in seconds
    p_width = 5E-9 #pulse width in seconds
    user_input = "LIBERTY" #String to encode using the PPM scheme and desired key, change to "input() in the future"
    encode_string = [x for x in user_input]
    key_file = "G:/Python/Encode_Key.csv"
    #Run the encoder
    slots, times, keyread, Tg = Encode(key_file, encode_string, reprate, M, s_width)
    print("The slots are "+str(slots))
    print("The pulse times are"+str(times))

    #Generate pulse times from encoded data
    #Currently configured for SDG2X with 0.2 ns time steps
    data_length = 50000
    frequency = 100000
    amp = 1.8
    offset = 0.9
    timestep = 0.2E-9
    encoded_arb_file = 'G:/Python/Enc_Arb.csv'
    Header_dat = [["data length", data_length],["frequency",frequency],["amp",amp],["offset",offset],["phase",0],[" "," "],[" "," "],[" "," "],[" "," "],[" "," "],[" "," "],[" "," "],["xpos","value"]]
    ArbWave(encoded_arb_file, Header_dat, times, s_width, data_length, amp, timestep)



    
    
    
