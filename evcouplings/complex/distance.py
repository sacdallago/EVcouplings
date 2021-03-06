"""
Protocols for concatenating sequences based
on distance in genomes (DNA sequences).
DNA sequences are extracted from the EMBL ENA databse,
and may refer to whole genome sequences, contigs, and plasmids.

Authors:
  Anna G. Green
  Thomas A. Hopf
  Charlotta P.I. Schärfe
"""
import pandas as pd
import matplotlib.pyplot as plt


def get_distance(annotation_1, annotation_2):
    """
    Compute distance between two CDS locations on
    the same genome
    
    Parameters
    ----------
    annotation_1 : tuple of (int, int)
        genome start and end location for the first CDS
    annotation_2 : tuple of (int, int)
        genome start and end location for the first CDS
        
    Returns
    -------
    int
        Distance between gene 1 and gene 2 on the
        ENA genome
    """

    # extract the two locations from the annotation
    # sort each so that smaller genome position is first
    location_1 = sorted(annotation_1)
    location_2 = sorted(annotation_2)

    # sort the two annotations so that the one with
    # an earlier start site is first
    x, y = sorted((location_1, location_2))

    # if not overlapping, calculate the distance
    if x[0] <= x[1] < y[0]:
        return y[0] - x[1]

    # if overlapping, return 0
    return 0


def best_reciprocal_matching(possible_partners):
    """
    Amongst all possible pairings of CDSs
    for two monomer proteins, finds
    those where both sequences are closest 
    on the genome to each other

    Parameters
    ----------
    possible_partners : pd.DataFrame
        Columns : uniprot_id_1, uniprot_id_2, distance_between_genes
        Generated by the find_possible_partners function.
        Gives all pairs of uniprot identifiers from alignment 1 
        with every uniprot identifier from alignment 2 that is found in 
        the same genome, and the number of nucleotides between their
        corresponding coding DNA sequences (CDS)

    Returns
    -------
    pd.DataFrame
        Columns: uniprot_id_1, uniprot_id_2, distance_between_genes
        All pairings of uniprot identifiers that are reciprocally the 
        closest to one another in a genome.

    """
    # initialize list to store the matches
    id_pairing_list = []

    # group the table by first and second uniprot identifier
    id_group_1 = possible_partners.groupby("uniprot_id_1")
    id_group_2 = possible_partners.groupby("uniprot_id_2")

    # loop through all sequences in first alignment, and find the closest reciprocal
    # partner for each
    for uniprot_id_1 in id_group_1.groups.keys():

        # get the table that corresponds to the current uniprot id
        id_subset_1 = id_group_1.get_group(uniprot_id_1)

        # what is the closest sequence in second alignment (w.r.t. to genome distance)?
        _index_of_closest = id_subset_1["distance"].idxmin()
        closest_to_uniprot_1 = id_subset_1.loc[_index_of_closest]["uniprot_id_2"]

        # get all of the rows that contain the closest hit in the second alignment
        id_subset_2 = id_group_2.get_group(closest_to_uniprot_1)

        # find the closest sequence in first alignment to the above sequence in second alignment
        _index_of_closest = id_subset_2["distance"].idxmin()
        closest_to_uniprot_2 = id_subset_2.loc[_index_of_closest]["uniprot_id_1"]

        # check if matched sequences are reciprocally the closest on the genome
        if closest_to_uniprot_2 == uniprot_id_1:
            distance = id_subset_1["distance"].min()
            id_pairing_list.append((uniprot_id_1, closest_to_uniprot_1, distance))

    # convert the data to a pandas dataframe
    id_pairing = pd.DataFrame(
        id_pairing_list,
        columns=["uniprot_id_1", "uniprot_id_2", "distance"]
    )

    return id_pairing


def find_possible_partners(gene_location_table_1, gene_location_table_2):
    """
    Constructs a dataframe of all possible sequence pairings
    between the two monomer alignments. Best reciprocal matches
    will then be selected using best_reciprocal_matching().

    Parameters
    ----------
    gene_location_table_1: pd.DataFrame
        Dataframe of gene locations for the first
        protein, generated by extract_embl_annotation
    gene_location_table_2: pd.DataFrame
        Dataframe of gene locations for the second
        protein, generated by extract_embl_annotation

    Returns
    -------
    pd.DataFrame
        Columns: uniprot_id_1, uniprot_id_2, distance_between_genes
        Gives all pairs of uniprot identifiers from alignment 1
        with every uniprot identifier from alignment 2 that is found in
        the same genome, and the number of nucleotides between their
        corresponding coding DNA sequences (CDS)
    """

    possible_partners_list = []

    # drop any rows that are missing location information for the CDS
    gene_location_table_1.dropna(axis=0, inplace=True)
    gene_location_table_2.dropna(axis=0, inplace=True)

    # drop duplicate rows - speeds up calculation
    gene_location_table_1.drop_duplicates(inplace=True)
    gene_location_table_2.drop_duplicates(inplace=True)

    # group the gene location tables by genome ID
    location_groups_1 = gene_location_table_1.groupby("genome_id")
    location_groups_2 = gene_location_table_2.groupby("genome_id")

    # iterate over EMBL genomes found in the first alignment
    for genome in location_groups_1.groups.keys():

        # if the same genome is found in the second alignment
        if genome in location_groups_2.groups.keys():

            # extract the entries corresponding to the current genome
            gene_location_subset_1 = location_groups_1.get_group(genome)
            gene_location_subset_2 = location_groups_2.get_group(genome)

            # compare all pairs of CDSs 
            # that originate from the current genome
            # find the distances between all pairs
            for _, first_cds in gene_location_subset_1.iterrows():
                for _, second_cds in gene_location_subset_2.iterrows():
                    distance_between_genes = get_distance(
                        (  # location of the first cds
                            first_cds["gene_start"],
                            first_cds["gene_end"]
                        ),
                        (  # location of the second cds
                            second_cds["gene_start"],
                            second_cds["gene_end"]
                        ),
                    )

                    # get the uniprot ids corresponding to the two CDSs
                    uniprot_id_1 = first_cds["full_id"]
                    uniprot_id_2 = second_cds["full_id"]

                    possible_partners_list.append(
                        (uniprot_id_1, uniprot_id_2, distance_between_genes)
                    )

    possible_partners = pd.DataFrame(
        possible_partners_list,
        columns=["uniprot_id_1", "uniprot_id_2", "distance"]
    )

    return possible_partners


def plot_distance_distribution(id_pair_to_distance, outfile):
    """
    plots the distribution of genome distances. This is designed
    to run on the output of best_reciprocal_matching().
    
    Parameters
    ----------
    id_pair_to_distance : pd.DataFrame
        with columns uniprot_id_1, uniprot_id_2, distance_between_genes
    outfile : str
        path to file to save plot
    """
    
    distances = list(id_pair_to_distance["distance"])
    distances = sorted(distances)

    # Make sure that there is at least one non-nan distance
    # in the data frame
    if len(distances) == 0:
        raise ValueError(
            "No valid distances provided"
         )

    cdf = range(len(distances))

    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.gca()
    ax1.set_xscale("log")
    ax1.set_xlim(xmin=1, xmax=max(distances))
    ax1.set_ylabel("Number of sequences")
    ax1.set_xlabel("Genome distance (bases)")
    ax1.plot(distances, cdf)
    
    plt.savefig(outfile)
