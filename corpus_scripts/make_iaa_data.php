<?php
mb_internal_encoding('UTF-8');

@mkdir("iaa");

$gData=[];

function processFolder($n){
    global $gData;

    $csv="cross/data/metadata_${n}.tsv";
    if($n==0)$csv="final/metadata.tsv";

    $fin=fopen($csv,"r");
    $first=true;
    while( ($data=fgetcsv($fin, 4096, "\t", "\"", "\\"))!==false){
        if($first){$first=false;continue;}

        $fname=$data[0];
        if(empty($fname))continue;

        $complexity=$data[2];
        $rf=$data[3];
        $sentiment1=$data[4];
        $sentiment2=$data[5];
        $political=$data[6];

        $annotator=$n;
        if($n==0)$annotator=intval(substr($fname,0,3));

        if(!isset($gData[$annotator]))$gData[$annotator]=[];
        $gData[$annotator][$fname]=[$complexity, $rf, $sentiment1, $sentiment2, $political];

    }
    fclose($fin);

    echo "Processed $n\n";

}

echo "Processing folders\n";
for($n=0;$n<=5;$n++){
    processFolder($n);
}

echo "Total data: ".count($gData)."\n";
echo "Writing CSV\n";


for($n=1;$n<=5;$n++){
    $fout=fopen("iaa/metadata_${n}.tsv","w");
    fwrite($fout,implode("\t",[
        "ID","Complexity","Real_Fake","Sentiment1","Sentiment2","Political",
    ])."\n");
    foreach($gData[$n] as $k=>$data){
        fwrite($fout,implode("\t", array_merge([$k],$data))."\n");
    }
    fclose($fout);
}
