<?php
mb_internal_encoding('UTF-8');

@mkdir("cross/data");
@mkdir("cross/text");

$sentiMap=[
"Bucurie"=>"Joy", 
"Dragoste"=>"Love", 
"Frica"=>"Fear", 
"Manie"=>"Anger", 
"Surpriza"=>"Surprise", 
"Tristete"=>"Sadness"
];

$gData=[];
$exempluDone=false;

function processFolder($n){
    global $gData,$exempluDone,$sentiMap;

    $dir="cross/CROSS$n";
    $csv="cross/CROSS$n.csv";
    @mkdir("cross/text/$n");

    if(!is_dir($dir) || !is_file($csv)){
        echo "Invalid N=$n\n";
        return false;
    }

    $current=0;

    $fin=fopen($csv,"r");
    $first=true;
    while( ($data=fgetcsv($fin, 4096, ";", "\"", "\\"))!==false){
        if($first){$first=false;continue;}

        $fname=$data[0];
        if(empty($fname))continue;

        if(!is_file("$dir/$fname")){
            echo "WARN: Missing file: $dir/$fname\n";
            continue;
        }

        $source=trim($data[1]);
        $url=trim($data[2]);
        $text=trim($data[3]);
        $complexity=$data[4];
        $real_fake=$data[5];
        $sentiment1=$data[6];
        $sentiment2=$data[7];

        if(!isset($sentiMap[$sentiment2])){
            echo "WARNING: Invalid sentiment2 [$sentiment2]\n";
            continue;
        }
        $sentiment2=$sentiMap[$sentiment2];

        $political=$data[8];

        $current++;

        $ext=strtolower(substr($fname, strrpos($fname, ".")+1));
        $dst=strtolower(substr($fname, 0,strrpos($fname, ".")));
        //$dst=sprintf("%03d%05d",$n,$current);

        $img=getimagesize("$dir/$fname");
        if(!isset($img["channels"]))$img["channels"]=3;

        $fTextUppercase="No";
        $t1=mb_strtoupper($text);
        if($t1==$text)$fTextUppercase="Yes";

        $fTextLowercase="No";
        $t1=mb_strtolower($text);
        if($t1==$text)$fTextLowercase="Yes";

        $gData[]=[
            "id"=>$dst,
            "ext"=>$ext,
            "source"=>$source,
            "url"=>$url,
            "text"=>$text,
            "complexity"=>$complexity,
            "real_fake"=>$real_fake,
            "sentiment1"=>$sentiment1,
            "sentiment2"=>$sentiment2,
            "political"=>$political,
            "width"=>$img[0],
            "height"=>$img[1],
            "mime"=>$img["mime"],
            "channels"=>$img["channels"],
            "bits"=>$img["bits"],
            "filesize"=>filesize("$dir/$fname"),
            "textsizec"=>mb_strlen($text),
            "textsizeb"=>strlen($text),
            "fTextUppercase"=>$fTextUppercase,
            "fTextLowercase"=>$fTextLowercase,
        ];


        //copy("$dir/$fname","final/images/${dst}.${ext}");
        file_put_contents("cross/text/$n/${dst}.txt",$text);
    }
    fclose($fin);

    echo "Processed $n => $current\n";

}

echo "Processing folders\n";
for($n=1;$n<=5;$n++){
    $gData=[];
    processFolder($n);
    echo "Total data: ".count($gData)."\n";
    echo "Writing CSV\n";

    $fout=fopen("cross/data/metadata_${n}.tsv","w");
    fwrite($fout,implode("\t",[
        "ID","Extension","Complexity","Real_Fake","Sentiment1","Sentiment2","Political",
        "Width","Height","Channels","Mime","ImageFileSize","TextSizeChar","TextSizeBytes",
        "TextUppercase","TextLowercase"
    ])."\n");
    foreach($gData as $data){
        fwrite($fout,implode("\t",[
        $data["id"],$data["ext"],$data["complexity"],$data["real_fake"],$data["sentiment1"],$data["sentiment2"],$data["political"],
        $data["width"],$data["height"],$data["channels"],$data["mime"],$data["filesize"],$data["textsizec"],$data["textsizeb"],
        $data['fTextUppercase'],$data['fTextLowercase']
    ])."\n");
    }
    fclose($fout);
    echo "\n";
}
