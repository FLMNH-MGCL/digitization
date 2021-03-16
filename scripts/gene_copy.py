import sys


def throw_error(message):
    print("gene_copy.py error: ", message)
    sys.exit(-1)


class IBAEntry:
    def __init__(self, gene_code, inner_values, genus, species, consensus, sequence):
        self.gene_code = gene_code  # str
        self.inner_values = inner_values  # str[]
        self.genus = genus  # str
        self.species = species  # str
        self.consensus = consensus  # str
        self.sequence = sequence  # str

    # this allows me to print the object in a readable format. I am
    # manually structuring it exactly as it is read from the .fas file.
    def __str__(self):
        return "{}|{}|{}|{}||{}\n{}\n".format(
            self.gene_code,
            # this will join each element in the {inner_values} list as a string,
            # and use the | as the delimeter.
            # ex: "|".join(["a","b","c"]) -> "a|b|c"
            "|".join(self.inner_values),
            self.genus,
            self.species,
            self.consensus,
            self.sequence
        )

### STRUCTURE OF LABEL LINE ###
# >gene_code|this section has between 1-4 values separated by a pipe|Genus|species|consensus_delim
### ####################### ###

### EXAMPLE LABEL LINE AND SEQUENCE LINE PAIR ###
# >L618|510|Oenosandra|boisduvalii||comp0_consensus
# GCGATAATCCTGCTGGACACGCAGGGCGCGTTTGACAGCGAGTCGACGGTGCGCGACTGCGCCACCATCTTCGCTCTGGCCACCATGGTGTCCTCCGTGCTCATATACAACCTCTCGCAGAACATACAGGAGGACGACTTGCAGCA-----
### ######################################## ###


# this will store -> { species_name : IBAEntry[] }
species = dict()

# I am hard coding the file for this demo. Typically I'd just use argparser to create a
# nice CLI
with open("./FcC_AA_L618.fas", "r") as f:
    label = f.readline().strip()

    # loop condition is while a label line was collected
    while label:
        sequence = f.readline().strip()

        if not sequence:
            # Honestly you can also just break here instead of throwing an error.
            # It just depends on how you'd like to handle this edge case of having
            # the line for the label with no sequence data
            throw_error("no sequence data for {}".format(label))

        pieces = list(
            filter(
                # isolate each bit of text between |, excluding those that are either
                # none or empty strings. without this check, the double || at the end
                # before the consensus_delim would result in a bad value stored
                lambda piece: piece is not None and piece != '',
                label.split('|')
            )
        )

        # gene_code -> 1
        # inner_values -> 1-4
        # genus + species + consensus_delim -> 3
        # 1 + 1 + 3 -> 5 => minimum values
        if len(pieces) < 5:
            throw_error(
                "invalid .fas line, expected to unpack at least 5 pipe-delimited values"
            )

        # gene_code -> 1
        # inner_values -> 1-4
        # genus + species + consensus_delim -> 3
        # 1 + 4 + 3 -> 8 => maximum values
        elif len(pieces) > 8:
            throw_error(
                "invalid .fas line, expected to unpack at most 8 pipe-delimited values"
            )

        entry = IBAEntry(
            pieces[0],
            # I have 1-4 values starting at index 1 and potentially three more following (through to
            # the fourth-from-last index). This is why I am accessing the elements from
            # 1 to -4. I am storing as a list, since I don't know how many there may be.
            pieces[1::-4],
            pieces[-3],
            pieces[-2],
            pieces[-1],
            sequence
        )

        # this is based on what I interpreted the instructions to define a 'copy' as.
        # if there are two sequences for one species, this the copies are too divergent and not
        # accurate, and therefore should be excluded from the list? IF this is not the case
        # and I misinterpreted, then you could likely slightly alter this to work with the
        # true 'copy' condition.
        #
        # Since my assumption is based on the recurrance of a species, I just use a list
        # as my dictionary value. This way, I can check {len(list)} to see how many
        # occurrences I added
        if entry.species in species:
            species[entry.species].append(entry)
        else:
            species[entry.species] = [entry]

        label = f.readline().strip()

# This dictionary is isn't necessary. I added it because usually I do something with
# the failures. In this case, I just use the length of the dictionary to print how many
# items were excluded from the new output .fas file.
#
# You could just as easily done something like this if you just needed the count:
# exlusions = 0
#
# and then just increment this value each time an entry is excluded.
copies = dict()

with open("./out.fas", "w") as f:
    for (key, val) in species.items():
        # is a 'copy' and not written
        if len(val) > 1:
            copies[key] = val
        else:
            f.write(str(val[0]))

print(len(copies), "items were filtered from the original file.")
print("species filtered out:", ", ".join(list(copies.keys())))
