# Bibliography audit

Scope: `Overleaf/references.bib` (101 entries) plus the non-empty per-chapter files
`Overleaf/bib/ch{02,03,05,07,08,09,10,11,13,14,15,19,20,21,22,23}-extra.bib` (61 entries).
Total **162 entries**. Files `ch01, ch04, ch06, ch12, ch16, ch17, ch18, ch24, ch25` contain only the
header comment and were skipped.

Method: one web search per entry with the exact title in quotes plus first author's surname and year;
authors, title, venue, volume/number/pages and year compared with the returned records.

## Summary

| Status | Count |
|---|---|
| VERIFIED | 158 |
| DETAILS DIFFER | 4 |
| NOT FOUND | 0 |
| UNSURE | 0 |

## Entries that look fabricated or unfindable

**None.** Every one of the 162 entries resolves to a real, locatable publication with matching
bibliographic data. No invented authors, venues, volumes or years were found.

## Entries needing a correction (4)

| key | what to change |
|---|---|
| `stern2019mapf` | last two authors are swapped — should end `... Kumar, T. K. Satish and Boyarski, Eli and Bart{\'a}k, Roman` |
| `ren2007information` | title is truncated — full title is `Information Consensus in Multivehicle Cooperative Control: Collective Group Behavior Through Local Interaction` |
| `bullo2009distributed` | title is truncated — full title is `Distributed Control of Robotic Networks: A Mathematical Approach to Motion Coordination Algorithms` |
| `hagberg2008networkx` | wrong entry type — it is a conference paper, not a journal article: use `@inproceedings` with `booktitle = {Proceedings of the 7th Python in Science Conference (SciPy 2008)}`, `address = {Pasadena, CA}` (author/pages/year are correct) |

## Optional additions (data verified, field simply absent)

`likhachev2003ara` pages 767--774 · `harabor2011jps` pages 1114--1119 ·
`andreychuk2019ccbs` pages 39--45 · `bennewitz2002finding` pages 89--99 ·
`li2019improved` pages 442--449 · `li2020pairwise` pages 193--201 ·
`felner2011position` pages 47--51, volume 2, number 1 · `stentz1995focussed` pages 1652--1659 ·
`surynek2009novel` pages 3613--3619 · `brock1999global` pages 341--346 ·
`connolly1990laplace` pages 2102--2106 · `jeroslow1974trivial` pages 105--109 ·
`ren2007distributed` pages 1002--1033 · `lerner2007crowds` pages 655--664 ·
`bengio2015scheduled` pages 1171--1179 · `douc2005comparison` pages 64--69 ·
`vaswani2017attention` pages 5998--6008.

## Full table

| key | status | notes / corrected fields | source |
|---|---|---|---|
| cormen2009clrs | VERIFIED | Cormen, Leiserson, Rivest, Stein; *Introduction to Algorithms*, 3rd ed., MIT Press, 2009; ISBN 9780262033848 | https://mitpress.mit.edu/9780262033058/introduction-to-algorithms/ |
| russell2020aima | VERIFIED | Russell & Norvig, 4th ed., Pearson, 2020; ISBN 0-13-461099-7 | https://www.pearson.com/en-us/subject-catalog/p/Russell-Artificial-Intelligence-A-Modern-Approach-4th-Edition/P200000003500 |
| lavalle2006planning | VERIFIED | LaValle, Cambridge University Press, 2006; ISBN 978-0-521-86205-9 | https://www.cambridge.org/core (via https://www.amazon.com/Planning-Algorithms-Steven-M-LaValle/dp/0521862051) |
| choset2005principles | VERIFIED | Choset, Lynch, Hutchinson, Kantor, Burgard, Kavraki, Thrun; MIT Press, 2005; ISBN 0-262-03327-5 | https://mitpress.mit.edu/9780262033275/principles-of-robot-motion/ |
| thrun2005probabilistic | VERIFIED | Thrun, Burgard, Fox; MIT Press, 2005; ISBN 978-0-262-20162-9 | https://direct.mit.edu/artl/article/14/2/227/2584/ |
| pearl1984heuristics | VERIFIED | Pearl, Addison-Wesley, 1984; ISBN 0201055945 | https://dl.acm.org/doi/abs/10.5555/525 |
| boyd2004convex | VERIFIED | Boyd & Vandenberghe, Cambridge University Press, 2004; ISBN 9780521833783 | https://www.cambridge.org/9780521833783 |
| nocedal2006numerical | VERIFIED | Nocedal & Wright, 2nd ed., Springer, 2006; ISBN 9780387303031 | https://www.amazon.com/Numerical-Optimization-Operations-Financial-Engineering/dp/0387303030 |
| goodfellow2016deep | VERIFIED | Goodfellow, Bengio, Courville; MIT Press, 2016; ISBN 9780262035613 | https://mitpress.mit.edu/9780262035613/deep-learning/ |
| sarkka2013bayesian | VERIFIED | Särkkä, Cambridge University Press, 2013; ISBN 978-1-107-03065-7 | https://www.cambridge.org/core/books/bayesian-filtering-and-smoothing/C372FB31C5D9A100F8476C1B23721A67 |
| barshalom2001estimation | VERIFIED | Bar-Shalom, Li, Kirubarajan; Wiley, 2001; ISBN 9780471416555 | https://www.wiley.com/en-us/Estimation+with+Applications+to+Tracking+and+Navigation:+Theory+Algorithms+and+Software-p-x000210749 |
| siciliano2016handbook | VERIFIED | eds. Siciliano & Khatib, 2nd ed., Springer, 2016; ISBN 978-3-319-32550-7 | https://dblp.org/db/reference/robo/robo2016.html |
| dijkstra1959note | VERIFIED | Numerische Mathematik 1:269--271, 1959; DOI 10.1007/BF01386390 | https://link.springer.com/article/10.1007/BF01386390 |
| hart1968formal | VERIFIED | IEEE Trans. Systems Science and Cybernetics 4(2):100--107, 1968 | https://dblp.org/rec/journals/tssc/HartNR68.html |
| hart1972correction | VERIFIED | SIGART Newsletter 37:28--29, 1972 | https://dblp.org/rec/journals/sigart/HartNR72.html |
| dechter1985generalized | VERIFIED | J. ACM 32(3):505--536, 1985; DOI 10.1145/3828.3830 | https://dl.acm.org/doi/10.1145/3828.3830 |
| pohl1970heuristic | VERIFIED | Artificial Intelligence 1(3--4):193--204, 1970; DOI 10.1016/0004-3702(70)90007-X | https://www.sciencedirect.com/science/article/abs/pii/000437027090007X |
| stentz1994optimal | VERIFIED | ICRA 1994, 3310--3317 | https://www.ri.cmu.edu/pub_files/pub1/stentz_anthony__tony__1994_1/stentz_anthony__tony__1994_1.pdf |
| koenig2002dstarlite | VERIFIED | AAAI 2002, 476--483 (AAAI prints the title as "D*Lite") | https://aaai.org/papers/00476-aaai02-072-d-lite/ |
| koenig2004lpa | VERIFIED | Artificial Intelligence 155(1--2):93--146, 2004 | https://www.sciencedirect.com/science/article/pii/S000437020300225X |
| koenig2005fast | VERIFIED | IEEE Trans. Robotics 21(3):354--363, 2005; DOI 10.1109/TRO.2004.838026 | https://dblp.org/rec/journals/trob/KoenigL05.html |
| likhachev2003ara | VERIFIED | NeurIPS 16 (2003); add pages 767--774 | https://proceedings.neurips.cc/paper/2003/hash/ee8fe9093fbbb687bef15a38facc44d2-Abstract.html |
| likhachev2005anytime | VERIFIED | ICAPS 2005, 262--271 | https://aaai.org/papers/icaps-05-027-anytime-dynamic-a-an-anytime-replanning-algorithm/ |
| ferguson2006field | VERIFIED | J. Field Robotics 23(2):79--101, 2006; DOI 10.1002/rob.20109 | https://onlinelibrary.wiley.com/doi/abs/10.1002/rob.20109 |
| harabor2011jps | VERIFIED | AAAI 2011; add pages 1114--1119; DOI 10.1609/aaai.v25i1.7994 | https://ojs.aaai.org/index.php/AAAI/article/view/7994 |
| phillips2011sipp | VERIFIED | ICRA 2011, 5628--5635 | https://www.semanticscholar.org/paper/7dba986bfff6cb4c7bffed3675a8cfbf0d08c1f9 |
| pearl1982studies | VERIFIED | IEEE TPAMI PAMI-4(4):392--399, 1982 | https://dl.acm.org/doi/10.1109/TPAMI.1982.4767270 |
| stern2019mapf | **DETAILS DIFFER** | last two authors swapped. Correct tail: `Kumar, T. K. Satish and Boyarski, Eli and Bart{\'a}k, Roman`. SoCS 2019, 151--158; DOI 10.1609/socs.v10i1.18510 — otherwise correct | https://arxiv.org/abs/1906.08291 |
| sharon2015cbs | VERIFIED | Artificial Intelligence 219:40--66, 2015; DOI 10.1016/j.artint.2014.11.006 | https://digitalcommons.du.edu/computer_science_faculty/7/ |
| sharon2012cbs | VERIFIED | AAAI 2012, 563--569 | https://ojs.aaai.org/index.php/AAAI/article/view/8140 |
| barer2014ecbs | VERIFIED | SoCS 2014, 19--27; DOI 10.1609/socs.v5i1.18315 | https://ojs.aaai.org/index.php/SOCS/article/view/18315 |
| boyarski2015icbs | VERIFIED | IJCAI 2015, 740--746; 7-author list matches | https://www.ijcai.org/Proceedings/15/Papers/110.pdf |
| felner2018adding | VERIFIED | ICAPS 2018, 83--87 | https://ojs.aaai.org/index.php/ICAPS/article/view/13883 |
| li2019symmetry | VERIFIED | AAAI 2019, 6087--6095 | https://ojs.aaai.org/index.php/AAAI/article/view/4565 |
| li2021eecbs | VERIFIED | AAAI 2021, 12353--12362 | https://dblp.org/rec/conf/aaai/0001RK21.html |
| felner2017search | VERIFIED | SoCS 2017, 29--37; DOI 10.1609/socs.v8i1.18423 | https://ojs.aaai.org/index.php/SOCS/article/view/18423 |
| silver2005cooperative | VERIFIED | AIIDE 2005, 117--122 | https://ojs.aaai.org/index.php/AIIDE/article/view/18726 |
| erdmann1987multiple | VERIFIED | Algorithmica 2:477--521, 1987; DOI 10.1007/BF01840371 | https://link.springer.com/article/10.1007/BF01840371 |
| vandenberg2005prioritized | VERIFIED | IROS 2005, 430--435 | https://www.researchgate.net/publication/224623306_Prioritized_motion_planning_for_multiple_robots |
| cap2015prioritized | VERIFIED | IEEE T-ASE 12(3):835--849, 2015; DOI 10.1109/TASE.2015.2445780 | https://arxiv.org/pdf/1409.2399 |
| ma2019searching | VERIFIED | AAAI 2019, 7643--7650 | https://ojs.aaai.org/index.php/AAAI/article/view/4758 |
| standley2010finding | VERIFIED | AAAI 2010, 173--178; DOI 10.1609/aaai.v24i1.7564 | https://ojs.aaai.org/index.php/AAAI/article/view/7564 |
| yu2013structure | VERIFIED | AAAI 2013, 1443--1449 | https://ojs.aaai.org/index.php/AAAI/article/view/8541 |
| yu2016optimal | VERIFIED | IEEE Trans. Robotics 32(5):1163--1177, 2016; DOI 10.1109/TRO.2016.2593448 | http://www.lavalle.pl/papers/YuLav16.pdf |
| surynek2010optimization | VERIFIED | AAAI 2010, 1261--1263 | https://ojs.aaai.org/index.php/AAAI/article/view/7767 |
| wagner2011mstar | VERIFIED | IROS 2011, 3260--3267 | http://biorobotics.ri.cmu.edu/papers/paperUploads/iros2011_wagner.pdf |
| wagner2015subdimensional | VERIFIED | Artificial Intelligence 219:1--24, 2015 | https://www.sciencedirect.com/science/article/pii/S0004370214001271 |
| luna2011push | VERIFIED | IJCAI 2011, 294--300 | https://dl.acm.org/doi/10.5555/2283396.2283446 |
| dewilde2014push | VERIFIED | JAIR 51:443--492, 2014 | https://jair.org/index.php/jair/article/view/10913 |
| honig2016mapf | VERIFIED | ICAPS 2016, 477--485; DOI 10.1609/icaps.v26i1.13796 | https://ojs.aaai.org/index.php/ICAPS/article/view/13796 |
| honig2018trajectory | VERIFIED | IEEE Trans. Robotics 34(4):856--869, 2018; DOI 10.1109/TRO.2018.2853613 | https://dl.acm.org/doi/10.1109/TRO.2018.2853613 |
| ma2017lifelong | VERIFIED | AAMAS 2017, 837--845 | https://www.ifaamas.org/Proceedings/aamas2017/pdfs/p837.pdf |
| fiorini1998motion | VERIFIED | IJRR 17(7):760--772, 1998 | https://journals.sagepub.com/doi/10.1177/027836499801700706 |
| vandenberg2008rvo | VERIFIED | ICRA 2008, 1928--1935 | https://gamma.cs.unc.edu/ORCA/ |
| vandenberg2011orca | VERIFIED | Robotics Research (ISRR), STAR vol. 70, 3--19, Springer 2011; DOI 10.1007/978-3-642-19457-3_1 | https://link.springer.com/chapter/10.1007/978-3-642-19457-3_1 |
| snape2011hrvo | VERIFIED | IEEE Trans. Robotics 27(4):696--706, 2011; DOI 10.1109/TRO.2011.2120810 | https://dl.acm.org/doi/10.1109/TRO.2011.2120810 |
| alonsomora2013optimal | VERIFIED | Distributed Autonomous Robotic Systems, STAR vol. 83, 203--216, Springer 2013; DOI 10.1007/978-3-642-32723-0_15 | https://link.springer.com/chapter/10.1007/978-3-642-32723-0_15 |
| fox1997dwa | VERIFIED | IEEE Robotics & Automation Magazine 4(1):23--33, 1997; DOI 10.1109/100.580977 | https://en.wikipedia.org/wiki/Dynamic_window_approach |
| khatib1986realtime | VERIFIED | IJRR 5(1):90--98, 1986 | https://journals.sagepub.com/doi/10.1177/027836498600500106 |
| koren1991potential | VERIFIED | ICRA 1991, 1398--1404 | https://www.semanticscholar.org/paper/07cc4371c8d3ddf7de0189f73227c3f0d896d66d |
| reynolds1987flocks | VERIFIED | SIGGRAPH 1987, 25--34; DOI 10.1145/37401.37406 | https://dblp.uni-trier.de/rec/conf/siggraph/Reynolds87.html |
| zhu2019chance | VERIFIED | IEEE RA-L 4(2):776--783, 2019 | https://repository.tudelft.nl/record/uuid:4c2e8664-4eb7-45ff-9e7e-a57ae643a371 |
| lavalle1998rrt | VERIFIED | TR 98-11, Computer Science Dept., Iowa State University, Oct. 1998 | https://lavalle.pl/rrtpubs.html |
| kuffner2000rrtconnect | VERIFIED | ICRA 2000, vol. 2, 995--1001; DOI 10.1109/ROBOT.2000.844730 | https://experts.illinois.edu/en/publications/rrt-connect-an-efficient-approach-to-single-query-path-planning/ |
| lavalle2001randomized | VERIFIED | IJRR 20(5):378--400, 2001; DOI 10.1177/02783640122067453 | https://journals.sagepub.com/doi/10.1177/02783640122067453 |
| karaman2011sampling | VERIFIED | IJRR 30(7):846--894, 2011; DOI 10.1177/0278364911406761 | https://journals.sagepub.com/doi/10.1177/0278364911406761 |
| gammell2014informed | VERIFIED | IROS 2014, 2997--3004 | https://arxiv.org/abs/1404.2334 |
| gammell2015bit | VERIFIED | ICRA 2015, 3067--3074; DOI 10.1109/ICRA.2015.7139620 | https://arxiv.org/abs/1405.5848 |
| kavraki1996prm | VERIFIED | IEEE Trans. Robotics and Automation 12(4):566--580, 1996 | https://web.ics.purdue.edu/~rvoyles/Classes/ROSprogramming/Kavraki_Latombe.PRM_PathPlanning.TRA96.pdf |
| kalman1960new | VERIFIED | Trans. ASME — J. Basic Engineering 82(1, Series D):35--45, 1960; DOI 10.1115/1.3662552 | https://www.cs.unc.edu/~welch/kalman/kalmanPaper.html |
| welch1995introduction | VERIFIED | TR 95-041, Dept. of Computer Science, UNC Chapel Hill, 1995 | https://www.cs.unc.edu/~welch/kalman/ (PDF: https://www.cs.yale.edu/homes/hudak-paul/CS474S01/kalman.pdf) |
| julier1997new | VERIFIED | Proc. SPIE 3068 (Signal Processing, Sensor Fusion, and Target Recognition VI), 182--193, 1997; DOI 10.1117/12.280797 | https://spie.org/Publications/Proceedings/Paper/10.1117/12.280797 |
| julier2004unscented | VERIFIED | Proceedings of the IEEE 92(3):401--422, 2004 | https://www.cs.ubc.ca/~murphyk/Papers/Julier_Uhlmann_mar04.pdf |
| wan2000unscented | VERIFIED | IEEE AS-SPCC 2000, 153--158 (Lake Louise, Oct. 2000) | https://ieeexplore.ieee.org/document/882463/ |
| gordon1993novel | VERIFIED | IEE Proceedings F 140(2):107--113, 1993; DOI 10.1049/ip-f-2.1993.0015 | https://digital-library.theiet.org/doi/10.1049/ip-f-2.1993.0015 |
| arulampalam2002tutorial | VERIFIED | IEEE Trans. Signal Processing 50(2):174--188, 2002; DOI 10.1109/78.978374 | https://dl.acm.org/doi/10.1109/78.978374 |
| hochreiter1997lstm | VERIFIED | Neural Computation 9(8):1735--1780, 1997; DOI 10.1162/neco.1997.9.8.1735 | https://direct.mit.edu/neco/article/9/8/1735/6109/ |
| alahi2016social | VERIFIED | CVPR 2016, 961--971 | https://www.cv-foundation.org/openaccess/content_cvpr_2016/html/Alahi_Social_LSTM_Human_CVPR_2016_paper.html |
| gupta2018social | VERIFIED | CVPR 2018, 2255--2264 | https://openaccess.thecvf.com/content_cvpr_2018/html/Gupta_Social_GAN_Socially_CVPR_2018_paper.html |
| vaswani2017attention | VERIFIED | NeurIPS 30 (2017); optional pages 5998--6008 | https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html |
| giuliari2021transformer | VERIFIED | ICPR, 10335--10342. Note: DBLP indexes the conference as ICPR 2020; it was held Jan. 2021 and the IEEE proceedings carry 2021 — either year is defensible, keep 2021 for consistency | https://dblp.org/pid/226/4872.html |
| salzmann2020trajectron | VERIFIED | ECCV 2020, 683--700; DOI 10.1007/978-3-030-58523-5_40 | https://link.springer.com/chapter/10.1007/978-3-030-58523-5_40 |
| rudenko2020human | VERIFIED | IJRR 39(8):895--935, 2020; DOI 10.1177/0278364920917446 | https://journals.sagepub.com/doi/abs/10.1177/0278364920917446 |
| kingma2015adam | VERIFIED | ICLR 2015 (poster), San Diego; arXiv:1412.6980 | https://dblp.org/rec/journals/corr/KingmaB14.html |
| pellegrini2009you | VERIFIED | ICCV 2009, 261--268 | http://vision.cse.psu.edu/courses/Tracking/vlpr12/PellegriniNeverWalkAlone.pdf |
| rawlings2017mpc | VERIFIED | Rawlings, Mayne, Diehl; 2nd ed., Nob Hill Publishing, 2017 | https://sites.engineering.ucsb.edu/~jbraw/mpc/ |
| mayne2000constrained | VERIFIED | Automatica 36(6):789--814, 2000; DOI 10.1016/S0005-1098(99)00214-9 | https://www.semanticscholar.org/paper/abe3167ff50408ea3b89890f63526c1f2fbd7087 |
| garcia1989model | VERIFIED | Automatica 25(3):335--348, 1989; DOI 10.1016/0005-1098(89)90002-2 | https://dblp.org/rec/journals/automatica/GarciaPM89.html |
| borrelli2017predictive | VERIFIED | Borrelli, Bemporad, Morari; Cambridge University Press, 2017; ISBN 9781107016880 | https://www.cambridge.org/highereducation/books/predictive-control-for-linear-and-hybrid-systems/EF618BD7AFAF4D04B2044A0FD03D885A |
| schouwenaars2001mixed | VERIFIED | European Control Conference 2001 (Porto), 2603--2608 | https://faculty.kaust.edu.sa/en/publications/mixed-integer-programming-for-multi-vehicle-path-planning |
| richards2002aircraft | VERIFIED | American Control Conference 2002, vol. 3, 1936--1941; DOI 10.1109/ACC.2002.1023918 | https://research-information.bris.ac.uk/en/publications/aircraft-trajectory-planning-with-collision-avoidance-using-mixed/ |
| mellinger2011minimum | VERIFIED | ICRA 2011, 2520--2525 | https://www.researchgate.net/publication/224252786_Minimum_snap_trajectory_generation_and_control_for_quadrotors |
| olfatisaber2007consensus | VERIFIED | Proceedings of the IEEE 95(1):215--233, 2007 | https://arxiv.org/abs/1009.6050 |
| olfatisaber2006flocking | VERIFIED | IEEE TAC 51(3):401--420, 2006; DOI 10.1109/TAC.2005.864190 | https://hal.elte.hu/~vicsek/downloads/papers/flocking_tac06-engineering.pdf |
| olfatisaber2004consensus | VERIFIED | IEEE TAC 49(9):1520--1533, 2004 | http://www.cds.caltech.edu/~murray/preprints/om04-tac.pdf |
| ren2005consensus | VERIFIED | IEEE TAC 50(5):655--661, 2005 | https://intra.ece.ucr.edu/~ren/papers/reprints/IEEE_TAC05_reprint.pdf |
| ren2008distributed | VERIFIED | Springer (London), 2008, Communications and Control Engineering; DOI 10.1007/978-1-84800-015-5 | https://link.springer.com/book/10.1007/978-1-84800-015-5 |
| oh2015survey | VERIFIED | Automatica 53:424--440, 2015 | https://www.sciencedirect.com/science/article/abs/pii/S0005109814004038 |
| jadbabaie2003coordination | VERIFIED | IEEE TAC 48(6):988--1001, 2003 | https://arxiv.org/pdf/cs/0407021 |
| panerati2021learning | VERIFIED | IROS 2021, 7512--7519; DOI 10.1109/IROS51168.2021.9635857 | https://dl.acm.org/doi/10.1109/IROS51168.2021.9635857 |
| hagberg2008networkx | **DETAILS DIFFER** | conference paper, not a journal article: change `@article` to `@inproceedings`, `booktitle = {Proceedings of the 7th Python in Science Conference (SciPy 2008)}`, `address = {Pasadena, CA}`. Authors, pages 11--15 and year 2008 are correct | https://proceedings.scipy.org/articles/TCWV9851 |
| lozanoperez1983spatial | VERIFIED | IEEE Trans. Computers C-32(2):108--120, 1983; DOI 10.1109/TC.1983.1676196 | https://dl.acm.org/doi/10.1109/TC.1983.1676196 |
| fredman1987fibonacci | VERIFIED | J. ACM 34(3):596--615, 1987; DOI 10.1145/28869.28874 | https://dl.acm.org/doi/10.1145/28869.28874 |
| felner2011position | VERIFIED | SoCS 2011; add volume 2, number 1, pages 47--51; DOI 10.1609/socs.v2i1.18191 | https://ojs.aaai.org/index.php/SOCS/article/view/18191 |
| sun2010moving | VERIFIED | AAMAS 2010 (Toronto, May 2010), Sun, Yeoh, Koenig | https://www.ifaamas.org/Proceedings/aamas2010/pdf/01%20Full%20Papers/01_02_FP_0035.pdf |
| stentz1995focussed | VERIFIED | IJCAI 1995; add pages 1652--1659 | https://dl.acm.org/doi/10.5555/1643031.1643113 |
| kornhauser1984pebble | VERIFIED | FOCS 1984, 241--250; DOI 10.1109/SFCS.1984.715921 | https://dl.acm.org/doi/10.1109/SFCS.1984.715921 |
| sartoretti2019primal | VERIFIED | IEEE RA-L 4(3):2378--2385, 2019; DOI 10.1109/LRA.2019.2903261 | https://par.nsf.gov/biblio/10179955 |
| andreychuk2019ccbs | VERIFIED | IJCAI 2019; add pages 39--45 | https://www.researchgate.net/publication/334844099_Multi-Agent_Pathfinding_with_Continuous_Time |
| bennewitz2002finding | VERIFIED | Robotics and Autonomous Systems 41(2--3), 2002; add pages 89--99 | https://www.sciencedirect.com/science/article/abs/pii/S0921889002002567 |
| sharon2013icts | VERIFIED | Artificial Intelligence 195:470--495, 2013 | https://www.sciencedirect.com/science/article/pii/S0004370212001543 |
| li2019improved | VERIFIED | IJCAI 2019; author order Li, Felner, Boyarski, Ma, Koenig confirmed; add pages 442--449; DOI 10.24963/ijcai.2019/63 | https://cris.bgu.ac.il/en/publications/improved-heuristics-for-multi-agent-path-finding-with-conflict-ba |
| li2020pairwise | VERIFIED | ICAPS 2020; add pages 193--201 | https://ojs.aaai.org/index.php/ICAPS/article/view/6661 |
| thayer2011bounded | VERIFIED | IJCAI 2011, Thayer & Ruml | https://www.ijcai.org/Proceedings/11/Papers/119.pdf |
| standley2011complete | VERIFIED | IJCAI 2011, 668--673 | https://www.ijcai.org/Proceedings/11/Papers/118.pdf |
| ferner2013odrmstar | VERIFIED | ICRA 2013, 3854--3859 | https://www.semanticscholar.org/paper/e5c34a7ca12f2eb4125f073234069e7bc678e2b3 |
| wilson1974graph | VERIFIED | J. Combinatorial Theory Series B 16(1):86--96, 1974; DOI 10.1016/0095-8956(74)90098-7 | https://www.sciencedirect.com/science/article/pii/0095895674900987 |
| surynek2009novel | VERIFIED | ICRA 2009 (Kobe); add pages 3613--3619 | https://link.springer.com/chapter/10.1007/978-3-642-32695-0_50 |
| deberg2008computational | VERIFIED | de Berg, Cheong, van Kreveld, Overmars; 3rd ed., Springer, 2008; ISBN 9783540779735 | https://dblp.org/rec/books/lib/BergCKO08.html |
| seidel1991small | VERIFIED | Discrete & Computational Geometry 6(3):423--434, 1991 | https://eudml.org/doc/131168 |
| brock1999global | VERIFIED | ICRA 1999, vol. 1; add pages 341--346 | http://robotics.stanford.edu/~oli/gdw.html |
| ogren2005convergent | VERIFIED | IEEE Trans. Robotics 21(2):188--195, 2005; DOI 10.1109/TRO.2004.838008 | https://ieeexplore.ieee.org/document/1416970/ |
| rimon1992exact | VERIFIED | IEEE Trans. Robotics and Automation 8(5):501--518, 1992 | https://repository.upenn.edu/ese_papers/323 |
| koditschek1990navigation | VERIFIED | Advances in Applied Mathematics 11(4):412--442, 1990 | https://www.semanticscholar.org/paper/b80b040e6e9fd83a5c1018a3425c4c2143899e02 |
| ge2000new | VERIFIED | IEEE Trans. Robotics and Automation 16(5):615--620, 2000 | https://ieeexplore.ieee.org/document/880813/ |
| connolly1990laplace | VERIFIED | ICRA 1990; add pages 2102--2106 | https://courses.cs.washington.edu/courses/cse599j/12sp/papers/Connolly.pdf |
| barraquand1991distributed | VERIFIED | IJRR 10(6):628--649, 1991; DOI 10.1177/027836499101000604 | https://journals.sagepub.com/doi/10.1177/027836499101000604 |
| arasaratnam2009cubature | VERIFIED | IEEE TAC 54(6):1254--1269, 2009 | https://www.semanticscholar.org/paper/b4226bae9693793ae9eb41c9886ead455f5f2cd1 |
| crisan2002survey | VERIFIED | IEEE Trans. Signal Processing 50(3):736--746, 2002; DOI 10.1109/78.984773 | https://www.cs.ubc.ca/~arnaud/crisan_doucet_survey.pdf |
| doucet2001sequential | VERIFIED | eds. Doucet, de Freitas, Gordon; Springer, 2001; DOI 10.1007/978-1-4757-3437-9 | https://link.springer.com/book/10.1007/978-1-4757-3437-9 |
| kitagawa1996monte | VERIFIED | J. Computational and Graphical Statistics 5(1):1--25, 1996; DOI 10.1080/10618600.1996.10474692 | https://www.tandfonline.com/doi/abs/10.1080/10618600.1996.10474692 |
| blom1988imm | VERIFIED | IEEE TAC 33(8):780--783, 1988; DOI 10.1109/9.1299 | https://research.tudelft.nl/en/publications/the-interacting-multiple-model-algorithm-for-systems-with-markovi/ |
| douc2005comparison | VERIFIED | ISPA 2005 (Zagreb); add pages 64--69; DOI 10.1109/ISPA.2005.195385 | https://arxiv.org/pdf/cs/0507025 |
| gers2000learning | VERIFIED | Neural Computation 12(10):2451--2471, 2000; DOI 10.1162/089976600300015015 | https://direct.mit.edu/neco/article/12/10/2451/6415/ |
| werbos1990bptt | VERIFIED | Proceedings of the IEEE 78(10):1550--1560, 1990; DOI 10.1109/5.58337 | https://www.semanticscholar.org/paper/1a3d22599028a05669e884f3eaf19a342e190a87 |
| schoeller2020constant | VERIFIED | IEEE RA-L 5(2):1696--1703, 2020; DOI 10.1109/LRA.2020.2969925 | https://dblp.org/rec/journals/ral/SchollerALK20.html |
| lakshminarayanan2017ensembles | VERIFIED | NeurIPS 30 (2017) | https://proceedings.neurips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html |
| bishop1994mixture | VERIFIED | TR NCRG/94/004, Neural Computing Research Group, Aston University, 1994 | https://publications.aston.ac.uk/id/eprint/373/1/NCRG_94_004.pdf |
| bengio2015scheduled | VERIFIED | NeurIPS 28 (2015); add pages 1171--1179 | https://dblp.org/rec/conf/nips/BengioVJS15.html |
| lerner2007crowds | VERIFIED | Computer Graphics Forum 26(3), 2007; add pages 655--664; DOI 10.1111/j.1467-8659.2007.01089.x | https://onlinelibrary.wiley.com/doi/10.1111/j.1467-8659.2007.01089.x |
| kerrigan2000soft | VERIFIED | UKACC International Conference on Control 2000, Cambridge UK, Sept. 2000 (secondary citations give pages 2319--2327) | https://spiral.imperial.ac.uk/entities/publication/b1d59b69-3901-41f5-bb9f-f619319fa9dc |
| stellato2020osqp | VERIFIED | Mathematical Programming Computation 12(4):637--672, 2020; DOI 10.1007/s12532-020-00179-2 | https://web.stanford.edu/~boyd/papers/osqp.html |
| boyd2011admm | VERIFIED | Foundations and Trends in Machine Learning 3(1):1--122, 2011 | https://dblp.org/rec/journals/ftml/BoydPCPE11.html |
| landdoig1960automatic | VERIFIED | Econometrica 28(3):497--520, 1960 | https://www.econometricsociety.org/publications/econometrica/1960/07/01/automatic-method-solving-discrete-programming-problems |
| wolsey1998integer | VERIFIED | Wolsey, Wiley, 1998; ISBN 9780471283669 | https://onlinelibrary.wiley.com/doi/book/10.1002/9781119606475 |
| vielma2015mixed | VERIFIED | SIAM Review 57(1):3--57, 2015 | https://dspace.mit.edu/bitstream/handle/1721.1/96480/Vielma-2015-Mixed%20Integer%20Linear.pdf |
| huangfu2018parallelizing | VERIFIED | Mathematical Programming Computation 10(1):119--142, 2018 | https://dblp.uni-trier.de/rec/journals/mpc/HuangfuH18.html |
| karp1972reducibility | VERIFIED | in *Complexity of Computer Computations*, eds. Miller & Thatcher, Plenum Press, 1972, 85--103 | https://link.springer.com/chapter/10.1007/978-1-4684-2001-2_9 |
| jeroslow1974trivial | VERIFIED | Mathematical Programming 6, 1974; add pages 105--109; DOI 10.1007/BF01580225 | https://link.springer.com/article/10.1007/BF01580225 |
| fiedler1973algebraic | VERIFIED | Czechoslovak Mathematical Journal 23(2):298--305, 1973 | https://dml.cz/dmlcz/101168 |
| xiao2004fast | VERIFIED | Systems & Control Letters 53(1):65--78, 2004 | https://web.stanford.edu/~boyd/papers/pdf/fastavg.pdf |
| ren2007distributed | VERIFIED | Int. J. Robust and Nonlinear Control 17(10--11), 2007; add pages 1002--1033; DOI 10.1002/rnc.1147 | https://onlinelibrary.wiley.com/doi/abs/10.1002/rnc.1147 |
| ren2007information | **DETAILS DIFFER** | title truncated. Correct: `Information Consensus in Multivehicle Cooperative Control: Collective Group Behavior Through Local Interaction`. IEEE Control Systems Magazine 27(2):71--82, 2007 is correct | https://www.semanticscholar.org/paper/c92917c75a596fd27351cb70a5694b61f622863f |
| ji2007distributed | VERIFIED | IEEE Trans. Robotics 23(4):693--703, 2007; DOI 10.1109/TRO.2007.900638 | https://dl.acm.org/doi/abs/10.1109/tro.2007.900638 |
| mesbahi2010graph | VERIFIED | Mesbahi & Egerstedt, Princeton University Press, 2010 (Princeton Series in Applied Mathematics); ISBN 9780691140612 | https://www.semanticscholar.org/paper/72080c14258cf8ca884329d50fdbe51790670b5a |
| bullo2009distributed | **DETAILS DIFFER** | title truncated. Correct: `Distributed Control of Robotic Networks: A Mathematical Approach to Motion Coordination Algorithms`. Princeton University Press 2009, ISBN 978-0-691-14195-4 is correct | https://press.princeton.edu/books/hardcover/9780691141954/distributed-control-of-robotic-networks |
| anderson2008rigid | VERIFIED | IEEE Control Systems Magazine 28(6):48--63, 2008 | https://openresearch-repository.anu.edu.au/items/278dacc3-3b3c-4ac0-b266-661fe1362839 |
| krick2009stabilisation | VERIFIED | Int. J. Control 82(3):423--439, 2009; DOI 10.1080/00207170802108441 | https://www.tandfonline.com/doi/full/10.1080/00207170802108441 |
| yang2010decentralized | VERIFIED | Automatica 46(2):390--396, 2010 | https://dblp.org/rec/journals/automatica/YangFGLSS10.html |
| vicsek1995novel | VERIFIED | Physical Review Letters 75(6):1226--1229, 1995; DOI 10.1103/PhysRevLett.75.1226 | https://ui.adsabs.harvard.edu/abs/1995PhRvL..75.1226V/abstract |
| tanner2007flocking | VERIFIED | IEEE TAC 52(5):863--868, 2007; DOI 10.1109/TAC.2007.895948 | https://www.georgejpappas.org/wp-content/uploads/2024/04/TJP07-TAC.pdf |
| zavlanos2011graph | VERIFIED | Proceedings of the IEEE 99(9):1525--1540, 2011 | https://www.michaelmzavlanos.org/publications |
