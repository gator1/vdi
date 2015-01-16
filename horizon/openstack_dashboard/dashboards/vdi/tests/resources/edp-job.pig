A = load '$INPUT' using PigStorage(':') as (fruit: chararray);
B = foreach A generate com.vdibook.pig.Trim(fruit);
store B into '$OUTPUT' USING PigStorage();
