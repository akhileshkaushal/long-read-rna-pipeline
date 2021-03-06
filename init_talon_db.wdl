# ENCODE long read rna pipeline: initialize talon database
# Maintainer: Otto Jolanki

workflow init_talon_db {
    File annotation_gtf
    String annotation_name
    String ref_genome_name
    String output_prefix
    Int ncpu
    Int ramGB
    String disk

    call init_db { input:
        annotation_gtf = annotation_gtf,
        annotation_name = annotation_name,
        ref_genome_name = ref_genome_name,
        output_prefix = output_prefix,
        ncpu = ncpu,
        ramGB = ramGB,
        disk = disk,
    }
}

task init_db {
    File annotation_gtf
    String annotation_name
    String ref_genome_name
    String output_prefix
    Int ncpu
    Int ramGB
    String disk

    command {
        gzip -cd ${annotation_gtf} > anno.gtf
        rm ${annotation_gtf}
        python3.7 $(which initialize_talon_database.py) \
            --f anno.gtf \
            --a ${annotation_name} \
            --g ${ref_genome_name} \
            --o ${output_prefix}

        python3.7 $(which record_init_db_inputs.py) \
            --annotation_name ${annotation_name} \
            --genome ${ref_genome_name} \
            --outfile ${output_prefix}_talon_inputs.json
        }
    
    output {
        File database = glob("*.db")[0]
        File talon_inputs = glob("*_talon_inputs.json")[0]
           }

    runtime {
        cpu: ncpu
        memory: "${ramGB} GB"
        disks: select_first(["local-disk 100 SSD", disk])
        }
}